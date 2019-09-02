import logging
from datetime import datetime
import pprint
from flask import jsonify, request
from flask_jwt_extended import jwt_required
from passlib.hash import argon2
from typing import Union

from app import db
from vidb.models import User, Question, Answer, Index, Result, ResultComponent, ResultSubComponent
from app.views import UserView, AnswerView, ResultView
from app.api import bp
from app.api.errors import VI400Exception, VI404Exception
from app.auth.auth import check_user
from vicalc import VICalculator

from sqlalchemy.exc import IntegrityError

def str_to_datetime(ans: str) -> Union[datetime, None]:
    if ans:
        d = datetime.strptime(ans, "%Y-%m-%d-%H-%M-%S")
        # no tz info, assumed to be in UTC
        return d
    return None


# register a new user
# must have token
# must be vivendor to create viuser
@bp.route('/users', methods=['POST'])
@jwt_required
def new_user():
    user = check_user(('vivendor',))
    logging.info("in /users[POST]")

    credentials = None
    if request.is_json:
        credentials = request.get_json()
    if not credentials:
        # no parameters
        logging.error("new_user: no input supplied")
        raise VI400Exception("No input supplied.")

    try:
        email = credentials['email']
    except KeyError:
        logging.error("new_user: email must be provided")
        raise VI400Exception("Email must be provided.")
    try:
        postal_code = credentials['postalcode']
    except KeyError:
        logging.error("new_user: postal code must be provided")
        raise VI400Exception("Postal code must be provided.")
    try:
        gender = credentials['gender']
    except KeyError:
        logging.error("new_user: gender must be provided")
        raise VI400Exception("Gender must be provided.")
    try:
        first_name = credentials['firstname']
    except KeyError:
        logging.error("new_user: first name must be provided")
        raise VI400Exception("First name must be provided.")
    try:
        password = credentials['password']
    except KeyError:
        logging.error("new_user: password must be provided")
        raise VI400Exception("Password must be provided.")
    bdate = None
    try:
        birthdate = credentials['birthdate']
        bdate = datetime.strptime(birthdate, "%Y-%m-%d").date()
    except KeyError:
        logging.error("new_user: birth date must be provided")
        raise VI400Exception("Birth date must be provided.")

    nrole = 'viuser'  # can only create viuser through this interface

    xhash = argon2.hash(password)
    try:
        user = User(email=email, pword=xhash, birth_date=bdate,
                    postal_code=postal_code, gender=gender, first_name=first_name, role=nrole)
        # flush to get id
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        # already exists
        logging.error("new_user: user name exists %s", email)
        raise VI400Exception("User with specified email already exists.")
    ret_results = {'count': 1, 'data': [UserView.render(user)]}

    return jsonify(ret_results), 201


# get user data
# fresh token required
# must be owner of data
@bp.route('/users', methods=['GET'])
@jwt_required
def get_user():
    logging.info("in /users[GET]")
    user = check_user(('viuser',))
    ret_results = {'count': 1, 'data': [UserView.render(user)]}
    return jsonify(ret_results)


# modify user data
@bp.route('/users', methods=['PATCH'])
@jwt_required
def modify_user():
    logging.info("in /users[PATCH]")
    user = check_user(('viuser',))
    # can only change email
    credentials = None
    if request.is_json:
        credentials = request.get_json()
    if not credentials:
        # no parameters
        logging.error("no input supplied")
        raise VI400Exception("No input supplied.")

    try:
        user.postal_code = credentials['postalcode']
    except KeyError:
        pass
    try:
        user.gender = credentials['gender']
    except KeyError:
        pass
    try:
        user.first_name = credentials['firstname']
    except KeyError:
        pass
    try:
        email = credentials['email']
        if email != user.email:
            # email (primary key) is changing
            if User.query.filter_by(email=email).exists():
                # user with this email already exists
                logging.error("user name exists")
                raise VI400Exception("User with specified email already exists.")
            user.email = email
    except KeyError:
        pass
    try:
        password = credentials['password']
        user.pword = argon2.hash(password)
        # logout user so they have to log in again with new password
        for token in user.tokens:
            token.revoked = True
    except KeyError:
        pass
    try:
        birthdate = credentials['birthdate']
        user.birth_date = datetime.strptime(birthdate, "%Y-%m-%d").date()
    except KeyError:
        pass

    db.session.add(user)
    db.session.commit()

    ret_results = {'count': 1, 'data': [UserView.render(user)]}
    return jsonify(ret_results)


# delete user data
@bp.route('/users', methods=['DELETE'])
@jwt_required
def delete_user():
    logging.info("in /users[DELETE]")
    user = check_user(('viuser',))
    # logout first
    for token in user.tokens:
        token.revoked = True
    # deletes ALL user data - user record, all answers and results
    user.delete()
    return jsonify(
        {'count': 1, 'data': [{'type': 'Message', 'msg': "Successfully deleted user {} out".format(user.email)}]})


# get answer set for user
# filters as url parameters - as-of-time, question
# as-of-time - latest answer for each question before this time
# question - all answers for question
# question and as-of-time - latest answer for question before time
@bp.route('/users/answers', methods=['GET'])
@jwt_required
def answers_for_user():
    logging.info("in /users/answers[GET]")

    # authenticate user
    user = check_user(('viuser',))
    # only artifacts owned by this user are ever returned
    answers = user.answers

    # this parameter can be a question name or not provided
    # if not provided answers for all questions (possibly qualified by index) are returned
    question_id = request.args.get('question')
    if question_id:
        question = Question.query.get(question_id)
        if not question:
            raise VI404Exception("No Question with the specified id was found.")
        answers = answers.filter(lambda a: a.question == question)

    # get index
    idx = Index.query.get(bp.config['INDEX'])
    if not idx:
        raise VI404Exception("No Index with the specified id was found.")
    answers = answers.filter(lambda a: idx in a.indexes)

    # this parameter can be a datetime string or not provided
    # pretty much required for useful answers unless question is specified
    aod = request.args.get('as-of-time', type=str_to_datetime)
    if aod:
        answers = answers.filter(lambda a: a.time_received <= aod).order_by(Answer.question, desc(Answer.time_received))
        manswers = {}
        # assume current answers are ordered by question and time received descending
        for answer in answers:
            if answer.question not in manswers:
                manswers[answer.question] = answer
        answers = manswers.values()

    ret_answers = {'count': len(answers), 'data': [AnswerView.render(a) for a in answers]}
    return jsonify(ret_answers)


# add a new answer(s) for a user
# answers in POST data
@bp.route('/users/answers', methods=['POST'])
@jwt_required
def add_answers_for_user():
    logging.info("in /users/answers[POST]")
    # truncate to second precision
    trecv = datetime.utcnow().replace(microsecond=0)

    # authorize user, will abort if auth fails
    user = check_user(('viuser',))

    data = None
    if request.is_json:
        data = request.get_json()
    if not data:
        # no parameters
        logging.error("no input supplied")
        raise VI400Exception("No input supplied.")

    logging.debug("data - %s" % pprint.pformat(data, indent=4))

    try:
        answers = data['answers']
    except KeyError:
        # no parameters
        logging.error("no answers supplied")
        raise VI400Exception("No answers supplied.")

    # get index
    idx = Index.query.get(bp.config['INDEX'])
    if not idx:
        raise VI404Exception("No Index with the specified id was found.")

    # load the components
    idx.index_components.load()

    ret_answers = []
    for question_name in answers.keys():
        # validate answers here before saving
        # empty answers are not saved
        # all answers are strings so this tests for empty string or None
        if answers[question_name]:
            question = Question.query.get(question_name)
            if not question:
                # warning - answer for question that does not exist
                raise VI404Exception("No Question with the specified id was found.")
            # load related sub components
            question.index_sub_components.load()

            # create Answer
            answer = Answer(question=question, time_received=trecv, answer=answers[question_name], user=user)
            db.session.add(answer)
            ret_answers.append(answer)

    # flush to get ids assigned before rendering
    db.session.commit()

    ranswers = {'count': len(ret_answers), 'data': [AnswerView.render(a) for a in ret_answers]}
    return jsonify(ranswers), 201


# get answer statistics for user
@bp.route('/users/answers/counts', methods=['GET'])
@jwt_required
def answer_counts_for_user():
    logging.info("in /users/answers/counts[GET]")

    # authenticate user
    user = check_user(('viuser',))

    answers = user.answers

    # get index
    idx = Index.query.get(bp.config['INDEX'])
    if not idx:
        raise VI404Exception("No Index with the specified id was found.")
    answers = answers.filter(lambda a: idx in a.indexes)

    counts = {bp.config['INDEX']: {'total': 0, 'answered': 0}}
    for c in idx.index_components:
        counts[c.name] = {'total': 0, 'answered': 0}
        for q in c.questions:
            counts[c.name]['total'] += 1
            counts[bp.config['INDEX']]['total'] += 1
            qanswers = answers.filter(lambda a: a.question == q)
            if len(qanswers) > 0:
                counts[c.name]['answered'] += 1
                counts[bp.config['INDEX']]['answered'] += 1

    ret_answers = {'count': 1, 'data': [counts]}
    return jsonify(ret_answers)


# get results for user
# filters as url parameters - as-of-time
@bp.route('/users/results', methods=['GET'])
@jwt_required
def results_for_user():
    logging.info("in /users/results[GET]")
    trecv = datetime.utcnow().replace(microsecond=0)

    # authenticate user
    user = check_user(('viuser',))
    results = user.results

    # get index
    idx = Index.query.get(bp.config['INDEX'])
    if not idx:
        raise VI404Exception("No Index with the specified id was found.")

    # this parameter can be a datetime string or not provided
    aod = request.args.get('as-of-time', type=str_to_datetime, default=trecv)
    numpts = request.args.get('numpts', type=int, default=1)
    results = results.filter(lambda r: r.index == idx and r.time_generated <= aod).order_by(
        lambda r: desc(r.time_generated))[:numpts]
    ret_results = [ResultView.render(r) for r in results]
    rresults = {'count': len(ret_results), 'data': ret_results}
    return jsonify(rresults)


# calc new index for user
@bp.route('/users/results', methods=['POST'])
@jwt_required
def create_index_for_user():
    logging.info("in /users/results[POST]")
    trecv = datetime.utcnow().replace(microsecond=0)

    # authenticate user
    user = check_user(('viuser',))

    aod = None
    data = None
    if request.is_json:
        data = request.get_json()
    if not data:
        aod = trecv
    elif 'as-of-time' not in data:
        aod = trecv
    else:
        aod = str_to_datetime(data['as-of-time'])

    idx = Index.query.get(bp.config['INDEX'])
    if not idx:
        raise VI404Exception("No Index with the specified id was found.")

    questions = idx.questions
    answers = {}
    found_at_least_one = False
    # questions now holds all the questions defined
    # map questions by name and create null answer for each question
    for question in questions:
        answers[question.name] = None
        # get the latest answer for this question and user
        lanswers = question.answers.filter(
            lambda a: a.user == user and a.time_received <= aod).order_by(
            lambda a: desc(a.time_received))[:1]
        if lanswers:
            found_at_least_one = True
            answers[question.name] = lanswers[0]

    if not found_at_least_one:
        # no answers in db
        logging.warning("Generating Result with no answers")

    ret_answers = {k: getattr(v, "answer") if v else '' for k, v in answers.items()}

    bdate = user.birth_date
    # calculate score
    logging.info('create_index_for_user: creating index for %s', user.email)
    # add birthdate to answers
    ret_answers['BirthDate'] = bdate.strftime("%Y-%m-%d")
    ret_answers['Gender'] = user.gender
    score = VICalculator.vi_points(ret_answers)

    # create the result linked to index
    logging.info("create_index_for_user: creating Result for %s", user.email)

    res = Result(time_generated=aod, user=user, points=score['INDEX'],
                 maxforanswered=score['MAXFORANSWERED'], index=idx)

    # link answer objects to result
    logging.info("create_index_for_user: Updating Answers - linking to Result for %s", user.email)
    for answer in answers.values():
        if answer:
            res.answers.add(answer)

    # create and link index components
    logging.info("create_index_for_user: Saving Result Components for %s", user.email)
    for icname, icscore in score['COMPONENTS'].items():
        idxcomp = idx.index_components.filter(lambda i: i.name == icname).get()
        ic = ResultComponent(points=icscore['POINTS'],
                             maxforanswered=icscore['MAXFORANSWERED'], result=res, index_component=idxcomp)
        for scname, scscore in icscore['COMPONENTS'].items():
            idxsubcomp = idxcomp.index_sub_components.filter(lambda i: i.name == scname).get()
            ResultSubComponent(points=scscore['POINTS'],
                               maxforanswered=scscore['MAXFORANSWERED'], result_component=ic,
                               index_sub_component=idxsubcomp)

    db.session.add(res)
    db.session.commit()

    rresults = {'count': 1, 'data': [ResultView.render(res)]}
    return jsonify(rresults), 201


#
# recommendation methods
#

@bp.route('/users/recommendations/<component_name>', methods=['GET'])
@jwt_required
def get_recommendations_for_result(component_name):
    logging.info("in /users/recommendations/%s[GET]", component_name)
    # authenticate user
    user = check_user(('viuser',))

    recommendations = []

    # get latest result
    result = None
    results = user.results

    idx = Index.query.get(bp.config['INDEX'])
    if not idx:
        raise VI404Exception("No Index with the specified id was found.")
    results = results.filter(lambda r: r.index == idx)

    if results:
        logging.info("get_recommendations: found results for %s", user.email)
        # this parameter can be a datetime string or not provided
        # pretty much required for useful answers unless question is specified
        aod = request.args.get('as-of-time', type=str_to_datetime)
        if not aod:
            # use current time
            aod = datetime.utcnow().replace(microsecond=0)
        logging.info("get_recommendations: filtering results for %s by %s", user.email, aod)
        results = results.filter(
            lambda r: r.time_generated <= aod).order_by(
            lambda r: desc(r.time_generated))[:1]
        result = results[0]
        if not result:
            # user has no results
            logging.error("User has no results meeting the criteria.")
            raise VI404Exception("User has no results meeting the criteria.")

        # so here we generate a block of text representing our recommendations for the given component of the latest result
        # first we check for unanswered questions - if above a certain threshold recommend answering more questions
        # then we look at each subcomponent and filter for those where points are below a certain threshold of maxanswered
        # We pick the three worst and provide recommendations for those

        # get specified component
        components = result.result_components.select(lambda c: c.name == component_name)[:]
        if not components:
            # component name in URL not correct
            logging.error("in recommendations - invalid category specified, %s", component_name)
            raise VI404Exception("Invalid category specified, %s" % component_name)
        component = components[0]

        aratio = component.maxforanswered / component.maxpoints
        logging.info("get_recommendations: found component %s with aratio %f for %s", component.name, aratio, user.email)
        if aratio < .5:
            # answer more questions
            logging.info("get_recommendations: generating recommendation for %s, with score %f", component.name,
                                                                               component.maxforanswered / component.maxpoints)
            recommendations.append({'type': 'Recommendation',
                                    'component': component.name,
                                    'text': 'One of the best ways to increase your Vitality Index score and make it more accurate is to answer more questions'})

        # look at the subcomponents
        # order them by % of maxforanswered points ascending
        # grab worst 3
        subs = component.result_sub_components
        logging.info("get_recommendations: found %d sub components for %s", subs.count(), user.email)
        subs = subs.filter(lambda s: s.maxforanswered > 0).order_by(lambda s: float(s.points) / float(s.maxforanswered))
        count = 0
        for sub in subs:
            if count >= 3:
                # get 3 recommendations
                break
            logging.info(
                "get_recommendations: generating recommendation for %s, with score %f", sub.name, sub.points / sub.maxforanswered)
            if sub.index_sub_component.recommendation:
                logging.info(
                    "get_recommendations: adding recommendation for %s", sub.name)
                recommendations.append({'type': 'Recommendation',
                                    'component': component.name,
                                    'text': sub.index_sub_component.recommendation})
                count += 1
            else:
                logging.info(
                    "get_recommendations: empty recommendation for %s", sub.name)

    return jsonify({'count': len(recommendations), 'data': recommendations})
