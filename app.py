"""
Primary app code. Listens to email and processes submissions
"""
import os
import logging
from datetime import datetime
from flask import Flask
from config import Config
app = Flask(__name__)
app.config.from_object(Config)

# set up logger
# make file unique
# we will be running multiple processes behind gunicorn
# we do not want all the processes writing to the same log file as this can result in garbled data in the file
# so we need a unique file name each time we run
# we will add date and time down to seconds (which will probably be the same for all processes)
# and add process id to get uniqueness
fparts = app.config['LOGFILE'].split('.')
bname = fparts[0]
ename = fparts[1]
nname = "%s.%s.%d.%s" % (bname, datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S"), os.getpid(), ename)
logfile = app.config['LOGDIR'] + nname
# create log directory if it does not exist
os.makedirs(app.config['LOGDIR'], 0o777, True)
# set up basic logging
logging.basicConfig(filename=logfile, level=app.config['LOGLEVEL'],
                    format='%(asctime)s - %(levelname)s - %(message)s')

import pprint
from datetime import date, timedelta, timezone
from passlib.hash import argon2
from typing import Tuple, Union
from flask import jsonify, request
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_jwt_extended import (
    JWTManager, jwt_required, jwt_refresh_token_required, decode_token, get_jwt_identity, 
    create_access_token, create_refresh_token
)
from sqlalchemy import func, cast, literal
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from vidb.models import User, Token, Question, Answer, Index, Result, ResultComponent, ResultSubComponent, IndexComponent, IndexSubComponent
from views import UserView, AnswerView, ResultView, ResultComponentView
from vicalc import VICalculator
from vimailserver import mail_tasks
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy(app)
jwt = JWTManager(app)


class VIServiceException(Exception):
    def __init__(self, message, status_code):
        Exception.__init__(self, message)
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        rv = {'error': self.message}
        return rv


class VI400Exception(VIServiceException):
    def __init__(self, message):
        super().__init__(message, 400)


class VI401Exception(VIServiceException):
    def __init__(self, message):
        super().__init__(message, 401)


class VI403Exception(VIServiceException):
    def __init__(self, message):
        super().__init__(message, 403)


class VI404Exception(VIServiceException):
    def __init__(self, message):
        super().__init__(message, 404)


class VI500Exception(VIServiceException):
    def __init__(self, message):
        super().__init__(message, 500)


def error_response(error, headers=None):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    if headers:
        response.headers = headers
    return response


@app.errorhandler(VI401Exception)
def handle_exception_401(error):
    return error_response(error, {'WWW-Authenticate': 'Bearer realm="access to VI backend"'})


@app.errorhandler(VIServiceException)
def handle_exception(error):
    db.session.rollback()
    return error_response(error)


@app.before_request
def before_request():
    # log actual full url of each call
    logging.debug("handling request to %s", request.url)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Token': Token,
            'Question': Question, 'Answer': Answer,
            'Result': Result, 'ResultComponent': ResultComponent, 'ResultSubComponent': ResultSubComponent,
            'Index': Index, 'IndexComponent': IndexComponent, 'IndexSubComponent': IndexSubComponent
            }


def str_to_datetime(ans: str) -> Union[datetime, None]:
    if ans:
        d = datetime.strptime(ans, "%Y-%m-%d-%H-%M-%S")
        # no tz info, assumed to be in UTC
        return d
    return None


def _epoch_utc_to_datetime(epoch_utc) -> datetime:
    """
    Helper function for converting epoch timestamps (as stored in JWTs) into
    python datetime objects (which are easier to use with sqlalchemy).
    """
    return datetime.fromtimestamp(epoch_utc, tz=timezone.utc)


def add_token_to_database(encoded_token, user: User) -> None:
    """
    Adds a new token to the database. It is not revoked when it is added.
    """
    decoded_token = decode_token(encoded_token)
    jti = decoded_token['jti']
    token_type = decoded_token['type']
    expires = _epoch_utc_to_datetime(decoded_token['exp'])
    revoked = False

    token = Token(jti=jti,
                  token_type=token_type,
                  user=user,
                  expires=expires,
                  revoked=revoked
                  )
    db.session.add(token)
    db.session.commit()


def is_token_revoked(decoded_token) -> bool:
    """
    Checks if the given token is revoked or not. Because we are adding all the
    tokens that we create into this database, if the token is not present
    in the database we are going to consider it revoked, as we don't know where
    it was created.
    """
    jti = decoded_token['jti']
    token = db.session.query(Token).filter(Token.jti == jti).one_or_none()
    if token:
        return token.revoked
    else:
        return True


def auth_user(email: str, pwd: str) -> User:
    logging.info('auth_user: authenticating user %s', email)
    # authenticate user
    if not email:
        # not authenticated
        logging.warning("auth_user: incorrect input - no email")
        raise VI401Exception("Please provide email.")
    if not pwd:
        # not authenticated
        logging.warning("auth_user: failed to authenticate")
        raise VI401Exception("Please provide password.")

    # lookup in db and authenticate
    # lookup User with email
    user = db.session.query(User).filter(User.email == email).one_or_none()
    if not user:
        # not authenticated
        logging.warning("auth_user: failed to authenticate %s", email)
        raise VI401Exception("Incorrect email or password")
    # verify password matches
    if not argon2.verify(pwd, user.pword):
        # not authenticated
        logging.warning("auth_user: failed to authenticate %s", email)
        raise VI401Exception("Incorrect email or password")
    return user


def check_user(role_set: Tuple[str, ...]) -> User:
    identity = get_jwt_identity()
    user_id = identity['id']
    logging.info('check_user: checking user %s', user_id)
    user = db.session.query(User).get(user_id)
    if not user:
        # not authenticated
        logging.error("check_user: failed to authenticate user id does not exist - %s", user_id)
        raise VI401Exception("Failed to authenticate user.")

    if user.role not in role_set:
        # no permission
        logging.warning("in check_user: insufficient privilege for user %s", user.email)
        raise VI403Exception("User does not have permission.")

    return user


# password recovery
@app.route('/reset-password-start', methods=['POST'])
def reset_password_start():
    logging.info("handling request to %s", request.url)
    logging.info("in reset-password-start[POST]")
    email = request.json.get('email', None)
    if not email:
        # not authenticated
        logging.error("reset_password: incorrect input - no email")
        raise VI400Exception("Please provide email.")
    url = request.json.get('url', None)
    if not url:
        # not authenticated
        logging.error("reset_password: incorrect input - no url")
        raise VI400Exception("Please provide url.")
    # lookup email in user db
    user = db.session.query(User).filter(User.email == email).one_or_none()
    if not user:
        logging.error("reset_password: email %s not found", email)
        raise VI404Exception("User not found.")
    logging.info("reset_password: starting reset of password for %s", user.email)
    # generate token
    s = URLSafeTimedSerializer(app.config['IDANGEROUSKEY'])
    token = s.dumps(user.id)
    # send email
    try:
        mail_tasks.send_password_reset.delay(email, url, token)
    except mail_tasks.send_password_reset.OperationalError as oe:
        logging.error("reset_password: error sending password reset email to %s", email)
        raise VI500Exception("error sending password reset email")
    logging.info("reset_password: reset email sent")
    return jsonify({'count': 1, 'data': [{'type': 'ResetToken', 'reset_token': token}]})


# password recovery
@app.route('/reset-password-finish', methods=['POST'])
def reset_password_finish():
    logging.info("handling request to %s", request.url)
    logging.info("in reset-password-finish[POST]")
    token = request.json.get('token', None)
    if not token:
        # not authenticated
        logging.error("reset password: incorrect input - no token")
        raise VI400Exception("Please provide token.")
    password = request.json.get('password', None)
    if not password:
        # not authenticated
        logging.error("reset password: incorrect input - no password")
        raise VI400Exception("Please provide password.")
    # decode token
    s = URLSafeTimedSerializer(app.config['IDANGEROUSKEY'])
    user_id = None
    try:
        user_id = s.loads(token, max_age=1800)
    except SignatureExpired:
        logging.error("reset password: token expired")
        raise VI401Exception("Token expired.")
    except BadSignature:
        logging.error("reset password: token invalid")
        raise VI400Exception("Token invalid.")
    # if not expired
    user = db.session.query(User).get(user_id)
    if not user:
        # not authenticated
        logging.error("reset password: User not found")
        raise VI404Exception("User not found.")
    logging.info("finishing reset of password for %s", user.email)
    user.pword = argon2.hash(password)
    for token in user.tokens:
        token.revoked = True
    db.session.add(user) # should cause tokens to be added/saved too
    db.session.commit()
    return jsonify(
        {'count': 1, 'data': [{'type': 'Message', 'msg': "Successfully updated password for {}".format(user.email)}]})


# Standard login endpoint. Will return a fresh access token and
# a refresh token
@app.route('/login', methods=['POST'])
def login():
    logging.info("handling request to %s", request.url)
    logging.info("in login[POST]")
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    user = auth_user(email, password)
    logging.info("login: logging in %s", user.email)
    user.last_login = datetime.utcnow().replace(microsecond=0)
    # Store the tokens in our store with a status of not currently revoked.
    access_token = create_access_token(identity={'id': user.id}, fresh=True)
    refresh_token = create_refresh_token(identity={'id': user.id})

    add_token_to_database(access_token, user)
    add_token_to_database(refresh_token, user)

    db.session.add(user)
    db.session.commit()

    ret = {'count': 1, 'data': [{'type': 'AccessToken', 'access_token': access_token, 'refresh_token': refresh_token}]}
    return jsonify(ret)


# Refresh token endpoint. This will generate a new access token from
# the refresh token.
@app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    logging.info("handling request to %s", request.url)
    logging.info("in refresh[POST]")
    user = check_user(('vivendor', 'viuser'))
    logging.info("refresh: refreshing %s", user.email)
    user.last_login = datetime.utcnow().replace(microsecond=0)
    new_token = create_access_token(identity={'id': user.id}, fresh=True)
    add_token_to_database(new_token, user)

    db.session.add(user)
    db.session.commit()

    ret = {'count': 1, 'data': [{'type': 'AccessToken', 'access_token': new_token, 'refresh_token': None}]}
    return jsonify(ret)


# Endpoint for revoking all the current users tokens
@app.route('/logout', methods=['DELETE'])
@jwt_required
def logout():
    logging.info("handling request to %s", request.url)
    logging.info("in logout[DELETE]")
    user = check_user(('vivendor', 'viuser'))
    logging.info("logout: logging out %s", user.email)
    for token in user.tokens:
        token.revoked = True

    db.session.add(user)
    db.session.commit()

    return jsonify(
        {'count': 1, 'data': [{'type': 'Message', 'msg': "Successfully logged out user {}".format(user.email)}]})


# Define our callback function to check if a token has been revoked or not
@jwt.token_in_blacklist_loader
def check_if_token_revoked(decoded_token):
    return is_token_revoked(decoded_token)


# register a new user
# must have token
# must be vivendor to create viuser
@app.route('/users', methods=['POST'])
@jwt_required
def new_user():
    logging.info("handling request to %s", request.url)
    logging.info("in new_user[POST]")

    user = check_user(('vivendor',))
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
@app.route('/users', methods=['GET'])
@jwt_required
def get_user():
    logging.info("handling request to %s", request.url)
    logging.info("in get_user[GET]")
    user = check_user(('viuser',))
    ret_results = {'count': 1, 'data': [UserView.render(user)]}
    return jsonify(ret_results)


# modify user data
@app.route('/users', methods=['PATCH'])
@jwt_required
def modify_user():
    logging.info("handling request to %s", request.url)
    logging.info("in modify_user[PATCH]")
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
            q = db.session.query(User).filter(User.email == email)
            if db.session.query(literal(True)).filter(q.exists()).scalar():
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
@app.route('/users', methods=['DELETE'])
@jwt_required
def delete_user():
    logging.info("handling request to %s", request.url)
    logging.info("in delete_user[DELETE]")
    user = check_user(('viuser',))
    # deletes ALL user data - user record, all answers and results
    db.session.delete(user)
    db.session.commit()

    return jsonify(
        {'count': 1, 'data': [{'type': 'Message', 'msg': "Successfully deleted user {} out".format(user.email)}]})


# get answer set for user
# default get the latest answer for user for each question in index
# filters as url parameters - as-of-time, question
# as-of-time - latest answer for each question before this time
# question - all answers for question ordered by time received desc
# question and as-of-time - latest answer for question before time
@app.route('/users/answers', methods=['GET'])
@jwt_required
def answers_for_user():
    logging.info("handling request to %s", request.url)
    logging.info("in answers_for_user[GET]")

    # authenticate user
    user = check_user(('viuser',))

    # get index
    idx = db.session.query(Index).get(app.config['INDEX'])
    if not idx:
        raise VI404Exception("No Index with the specified id was found.")

    answers = db.session.query(Answer).join(Question)
    answers = answers.join((IndexSubComponent, Question.index_sub_components)).join(IndexComponent)
    answers = answers.filter(Answer.user_id == user.id).filter(IndexComponent.index_name == idx.name)
    # this parameter can be a question name or not provided
    # if not provided answers for all questions (possibly qualified by index) are returned
    question_name = request.args.get('question')
    if question_name:
        question = None
        question = db.session.query(Question).get(question_name)
        if not question:
            raise VI404Exception("No Question with the specified id was found.")
        answers = answers.filter(Question.name == question_name)
    else:
        answers = answers.order_by(Question.name)
    answers = answers.order_by(Answer.time_received.desc())
    # this parameter can be a datetime string or not provided
    # pretty much required for useful answers unless question is specified
    aod = request.args.get('as-of-time', type=str_to_datetime)
    if aod:
        answers = answers.filter(Answer.time_received <= aod).all()
        manswers = {}
        # assume current answers are ordered by question and time received descending
        for answer in answers:
            if answer.question not in manswers:
                manswers[answer.question] = answer
        answers = manswers.values()
    else:
        answers = answers.all()

    ret_answers = {'count': len(answers), 'data': [AnswerView.render(a) for a in answers]}
    return jsonify(ret_answers)


# add a new answer(s) for a user
# answers in POST data
@app.route('/users/answers', methods=['POST'])
@jwt_required
def add_answers_for_user():
    logging.info("handling request to %s", request.url)
    logging.info("in add_answers_for_user[POST]")
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
    idx = db.session.query(Index).get(app.config['INDEX'])
    if not idx:
        raise VI404Exception("No Index with the specified id was found.")

    ret_answers = []
    for question_name in answers.keys():
        # validate answers here before saving
        # empty answers are not saved
        # all answers are strings so this tests for empty string or None
        if answers[question_name]:
            question = db.session.query(Question).get(question_name)
            if not question:
                # warning - answer for question that does not exist
                raise VI404Exception("No Question with the specified id was found.")

            # create Answer
            answer = Answer(question=question, time_received=trecv, answer=answers[question_name], user=user)
            db.session.add(answer)
            ret_answers.append(answer)

    db.session.commit()

    ranswers = {'count': len(ret_answers), 'data': [AnswerView.render(a) for a in ret_answers]}
    return jsonify(ranswers), 201


# get answer statistics for user
@app.route('/users/answers/counts', methods=['GET'])
@jwt_required
def answer_counts_for_user():
    logging.info("handling request to %s", request.url)
    logging.info("in answer_counts_for_user[GET]")

    # authenticate user
    user = check_user(('viuser',))

    # get index
    idx = db.session.query(Index).get(app.config['INDEX'])
    if not idx:
        raise VI404Exception("No Index with the specified id was found.")

    questions = db.session.query(Question).join((IndexSubComponent, Question.index_sub_components)).join(IndexComponent)
    questions = questions.filter(IndexComponent.index_name == idx.name).all()

    counts = {}
    counts[idx.name] = {'total': 0, 'answered': 0}
    for q in questions:
        # number of unanswered question
        answers = db.session.query(Answer).filter(Answer.user_id == user.id).filter(Answer.question_name == q.name).count()
        for isc in q.index_sub_components:
            if isc.indexcomponent_name not in counts:
                counts[isc.indexcomponent_name] = {'total': 0, 'answered': 0}
            counts[isc.indexcomponent_name]['total'] += 1
            counts[idx.name]['total'] += 1
            if answers > 0:
                counts[isc.indexcomponent_name]['answered'] += 1
                counts[idx.name]['answered'] += 1

    ret_answers = {'count': 1, 'data': [counts]}
    return jsonify(ret_answers)


# get results for user
# filters as url parameters - as-of-time
@app.route('/users/results', methods=['GET'])
@jwt_required
def results_for_user():
    logging.info("handling request to %s", request.url)
    logging.info("in results_for_user[GET]")
    trecv = datetime.utcnow().replace(microsecond=0)

    # authenticate user
    user = check_user(('viuser',))
    results = user.results

    # get index
    idx = db.session.query(Index).get(app.config['INDEX'])
    if not idx:
        raise VI404Exception("No Index with the specified id was found.")

    results = db.session.query(Result).filter(Result.user_id == user.id).filter(Result.index_name == idx.name)
    # this parameter can be a datetime string or not provided
    aod = request.args.get('as-of-time', type=str_to_datetime, default=trecv)
    numpts = request.args.get('numpts', type=int, default=1)
    results = results.filter(Result.time_generated <= aod).order_by(Result.time_generated.desc()).limit(numpts)
    ret_results = [ResultView.render(r) for r in results]
    rresults = {'count': len(ret_results), 'data': ret_results}
    return jsonify(rresults)


# calc new index for user
@app.route('/users/results', methods=['POST'])
@jwt_required
def create_index_for_user():
    logging.info("handling request to %s", request.url)
    logging.info("in create_index_for_user[POST]")
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

    aod = trecv

    # get index
    idx = db.session.query(Index).get(app.config['INDEX'])
    if not idx:
        raise VI404Exception("No Index with the specified id was found.")

    questions = db.session.query(Question).join((IndexSubComponent, Question.index_sub_components)).join(IndexComponent)
    questions = questions.filter(IndexComponent.index_name == idx.name)
    answers = {}
    found_at_least_one = False
    # questions now holds all the questions defined
    # map questions by name and create null answer for each question
    for question in questions:
        if not question.name in answers:
            answers[question.name] = None
            # get the latest answer for this question and user
            lanswers = db.session.query(Answer).filter(Answer.user_id == user.id).filter(Answer.time_received <= aod)
            lanswer = lanswers.filter(Answer.question == question).order_by(Answer.time_received.desc()).limit(1).first()
            if lanswer:
                found_at_least_one = True
                answers[question.name] = lanswer

    if not found_at_least_one:
        # no answers in db
        logging.warning("Generating Result with no answers")

    ret_answers = {k: getattr(v, "answer") if v else '' for k, v in answers.items()}

    bdate = user.birth_date
    # calculate score
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
            res.answers.append(answer)
            answer.results.append(res)

    # create and link index components
    logging.info("create_index_for_user: Saving Result Components for %s", user.email)
    for icname, icscore in score['COMPONENTS'].items():
        ic = ResultComponent(points=icscore['POINTS'],
                             maxforanswered=icscore['MAXFORANSWERED'], result=res, indexcomponent_name=icname)
        res.result_components.append(ic)
        for scname, scscore in icscore['COMPONENTS'].items():
            rsc = ResultSubComponent(points=scscore['POINTS'],
                                     maxforanswered=scscore['MAXFORANSWERED'], result_component=ic,
                                     indexsubcomponent_name=scname)
            ic.result_sub_components.append(rsc)

    db.session.add(res)
    db.session.commit()

    rresults = {'count': 1, 'data': [ResultView.render(res)]}
    return jsonify(rresults), 201


#
# recommendation methods
#

@app.route('/users/recommendations/<component_name>', methods=['GET'])
@jwt_required
def get_recommendations_for_result(component_name):
    logging.info("handling request to %s", request.url)
    logging.info("in get_recommendations_for_result[GET]")

    # authenticate user
    user = check_user(('viuser',))

    trecv = datetime.utcnow().replace(microsecond=0)
    recommendations = []

    idx = db.session.query(Index).get(app.config['INDEX'])
    if not idx:
        raise VI404Exception("No Index with the specified id was found.")

    results = db.session.query(Result).filter(Result.user_id == user.id).filter(Result.index_name == idx.name)
    results = results.filter(Result.time_generated <= trecv).order_by(Result.time_generated.desc()).limit(1)
    result = results.first()
    if not result:
        # user has no results
        logging.error("User has no results meeting the criteria.")
        raise VI404Exception("User has no results meeting the criteria.")

    # so here we generate a block of text representing our recommendations for the given component of the latest result
    # first we check for unanswered questions - if above a certain threshold recommend answering more questions
    # then we look at each subcomponent and filter for those where points are below a certain threshold of maxanswered
    # We pick the three worst and provide recommendations for those

    # get specified component
    components = db.session.query(ResultComponent).options(joinedload(ResultComponent.index_component), joinedload(ResultComponent.result_sub_components))
    components = components.filter(ResultComponent.result_id == result.id)
    components = components.filter(ResultComponent.indexcomponent_name == component_name)
    component = components.one_or_none()
    if not component:
        # component name in URL not correct
        logging.error("in recommendations - invalid category specified, %s", component_name)
        raise VI404Exception("Invalid category specified, %s" % component_name)

    aratio = component.maxforanswered / component.index_component.maxpoints
    logging.info("get_recommendations: found component %s with aratio %f for %s", component.indexcomponent_name, aratio, user.email)
    if aratio < .5:
        # answer more questions
        logging.info("get_recommendations: generating recommendation for %s", component_name)
        recommendations.append({'type': 'Recommendation',
                                'component': component_name,
                                'text': 'One of the best ways to increase your Vitality Index score and make it more accurate is to answer more questions'})

    # look at the subcomponents
    # order them by % of maxforanswered points ascending
    # grab worst 3
    subs = db.session.query(ResultSubComponent).join(IndexSubComponent)
    subs = subs.filter(ResultSubComponent.resultcomponent_id == component.id)
    # non empty recommendation
    subs = subs.filter(IndexSubComponent.recommendation != '')
    # some questions answered
    subs = subs.filter(ResultSubComponent.maxforanswered > 0)
    subs = subs.order_by(cast(ResultSubComponent.points, db.Float) / cast(ResultSubComponent.maxforanswered, db.Float))
    subs = subs.limit(3)
    for sub in subs:
        logging.info("get_recommendations: adding recommendation for %s", sub.indexsubcomponent_name)
        recommendations.append({'type': 'Recommendation',
                                'component': component_name,
                                'text': sub.index_sub_component.recommendation})

    return jsonify({'count': len(recommendations), 'data': recommendations})


# get result
@app.route('/results/<int:result_id>', methods=['GET'])
@jwt_required
def get_result(result_id):
    logging.info("handling request to %s", request.url)
    logging.info("in get_result[GET]")
    user = check_user(('viuser',))

    result = db.session.query(Result).get(result_id)
    if not result:
        # no result with this id
        raise VI404Exception("No Result with specified id.")

    if result.user != user:
        # resource exists but is not owned by, and therefor enot viewable by, user
        raise VI403Exception("User does not have permission.")
    rresults = {'count': 1, 'data': [ResultView.render(result)]}
    return jsonify(rresults)


# get result component
@app.route('/results/<int:result_id>/components/<int:component_id>', methods=['GET'])
@jwt_required
def get_result_component(result_id, component_id):
    logging.info("handling request to %s", request.url)
    logging.info("in get_result-component[GET]")
    # authenticate user
    user = check_user(('viuser',))
    result = db.session.query(Result).get(result_id)
    if not result:
        # no result with this id
        raise VI404Exception("No Result with specified id.")
    if result.user != user:
        # resource exists but is not owned by, and therefor enot viewable by, user
        raise VI403Exception("User does not have permission.")
    component = db.session.query(ResultComponent).get(component_id)
    if not component:
        # Component does not exist
        raise VI404Exception("no ResultComponent with specified id")
    if component.result != result:
        raise VI404Exception("no ResultComponent with specified id in this resource tree")
    rresults = {'count': 1, 'data': [ResultComponentView.render(component)]}
    return jsonify(rresults)


# get answers that went into a result
@app.route('/results/<int:result_id>/answers', methods=['GET'])
@jwt_required
def get_result_answers(result_id):
    logging.info("handling request to %s", request.url)
    logging.info("in get_result_answers[GET]")
    user = check_user(('viuser',))
    result = db.session.query(Result).options(joinedload(Result.answers)).get(result_id)
    if not result:
        # no result with this id
        raise VI404Exception("No Result with specified id.")

    if result.user != user:
        # resource exists but is not owned by, and therefor enot viewable by, user
        raise VI403Exception("User does not have permission.")

    ranswers = {'count': len(result.answers), 'data': [AnswerView.render(a) for a in result.answers]}
    return jsonify(ranswers)


#
# statistics methods
#

# provide average vi for certain criteria
# age, gender, location, component
# noinspection PyTypeChecker
@app.route('/statistics', methods=['GET'])
@jwt_required
def get_statistics():
    logging.info("handling request to %s", request.url)
    logging.info("in get_statistics[GET]")
    trecv = datetime.utcnow().replace(microsecond=0)
    td = date.today()
    # authenticate user
    user = check_user(('viuser',))

    agerange = request.args.get('agerange')
    gender = request.args.get('gender')
    region = request.args.get('region')

    result = None
    vgs = db.session.query(func.avg(Result.points), func.avg(Result.maxforanswered)).join(User)
    if gender:
        vgs = vgs.filter(User.gender == gender)
    if agerange:
        # age range is string like "x-y"
        ages = agerange.split('-')
        dplus = td - timedelta(days=int(ages[0]) * 365)
        dminus = td - timedelta(days=int(ages[1]) * 365)
        vgs = vgs.filter(User.birth_date.between(dminus, dplus))
    vg = vgs.filter(Result.time_generated == db.session.query(func.max(Result.time_generated)).filter(Result.user_id == User.id).correlate(User)).first()
    if vg:
        result = {
            'type': 'Result',
            'attributes': {
                'maxforanswered': vg[1],
                'maxpoints': 1000,
                'name': 'Vitality Index',
                'points': vg[0],
                'time_generated': trecv.strftime("%Y-%m-%d-%H-%M-%S"),
                'result_components': []
            }
        }

        vgs = db.session.query(IndexComponent.name,
                               func.avg(ResultComponent.points),
                               func.avg(ResultComponent.maxforanswered)).join(Result).join(User).join(IndexComponent).group_by(IndexComponent.name)
        if agerange:
            # age range is string like "x-y"
            ages = agerange.split('-')
            dplus = td - timedelta(days=int(ages[0]) * 365)
            dminus = td - timedelta(days=int(ages[1]) * 365)
            vgs = vgs.filter(User.birth_date.between(dminus, dplus))

        if gender:
            vgs = vgs.filter(User.gender == gender)

        vgs = vgs.filter(Result.time_generated == db.session.query(func.max(Result.time_generated)).filter(Result.user_id == User.id).correlate(User))

        for vg in vgs:
            rc = {
                'type': 'ResultComponent',
                'attributes': {
                    'maxforanswered': vg[2],
                    'name': vg[0],
                    'points': vg[1]
                }
            }
            result['attributes']['result_components'].append(rc)

        return jsonify({'count': 1, 'data': [result]})
    else:
        return jsonify({'count': 0, 'data': []})


# get answer
@app.route('/answers/<int:answer_id>', methods=['GET'])
@jwt_required
def get_answer(answer_id):
    logging.info("handling request to %s", request.url)
    logging.info("in get_answer[GET]")
    user = check_user(('viuser',))
    answer = db.session.query(Answer).get(answer_id)
    if not answer:
        # no answer with this id
        raise VI404Exception("No Answer with specified id.")

    if answer.user != user:
        # resource exists but is not owned by, and therefore not viewable by, user
        raise VI403Exception("User does not have permission.")

    ranswers = {'count': 1, 'data': [AnswerView.render(answer)]}
    return jsonify(ranswers)


# get results that used an answer
@app.route('/answers/<int:answer_id>/results', methods=['GET'])
@jwt_required
def get_answer_results(answer_id):
    logging.info("handling request to %s", request.url)
    logging.info("in get_answer_results[GET]")
    user = check_user(('viuser',))
    answer = db.session.query(Answer).options(joinedload(Answer.results)).get(answer_id)
    if not answer:
        # no answer with this id
        raise VI404Exception("No Answer with specified id.")

    if answer.user != user:
        # resource exists but is not owned by, and therefore not viewable by, user
        raise VI403Exception("User does not have permission.")

    rresults = {'count': len(answer.results), 'data': [ResultView.render(r) for r in answer.results]}
    return jsonify(rresults)



if __name__ == '__main__':
    app.run(host=app.config['WWWHOST'],
            port=app.config['WWWPORT'])