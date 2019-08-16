"""
Primary app code. Listens to email and processes submissions
"""
from flask import Flask
app = Flask(__name__)
# set up config
app.config.from_pyfile('./config/viservice.cfg')
import os
from datetime import datetime
# set up logger
# app.logger.setLevel(app.config['LOGLEVEL'])
logfile = app.config['LOGDIR'] + app.config['LOGNAME']
# check for existence and rotate
if os.path.isfile(logfile):
    # rename with time
    bname = app.config['LOGNAME'].split('.')[0]
    nname = "%s.%s.log" % (bname, datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S"))
    os.rename(logfile, os.path.join(app.config['LOGDIR'], nname))
else:
    # create log directory if it does not exist
    os.makedirs(app.config['LOGDIR'], 0o777, True)
import logging
# fh = logging.FileHandler(logfile)
# fh.setLevel(app.config['LOGLEVEL'])
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# fh.setFormatter(formatter)
# app.logger.addHandler(fh)

app.config['LOGLEVEL'] = os.getenv('LOGLEVEL')
# set up basic logging
logging.basicConfig(filename=logfile, level=app.config['LOGLEVEL'], format='%(asctime)s - %(levelname)s - %(message)s')

from typing import Tuple, Union
# logging
import logging
# pretty printing/formatting
import pprint
# date and time stuff
from datetime import timedelta
from passlib.hash import argon2

# Flask
from flask import jsonify, request
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity
)
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
# db interface
# noinspection PyUnresolvedReferences
from pony.orm import avg, max, between, desc

# VI algorithm
from vicalc import VICalculator

from blacklist_helpers import is_token_revoked, add_token_to_database
from views import *

# data model
from vidb.models import *
# email celery tasks
from vimailserver import mail_tasks

# configure from environment variables
# these will come in secure form from azure app settings in azure deployment
# database/pony
app.config['DBHOST'] = os.getenv('DBHOST')
app.config['DATABASE'] = os.getenv('DATABASE')
app.config['DBUSER'] = os.getenv('DBUSER')
app.config['DBPWD'] = os.getenv('DBPWD')
app.config['DBSSLMODE'] = os.getenv('DBSSLMODE')

# itsdangerous, jwt and flask keys
app.config['SECRET_KEY'] = os.getenv('FLASKKEY')
app.config['JWT_SECRET_KEY'] = os.getenv('JWTKEY')
app.config['IDANGEROUSKEY'] = os.getenv('ITSDANGEROUSKEY')

jwt = JWTManager(app)

index_id = "Vitality Index"

logging.info("connecting to database %s:%s:%s" % (app.config['DBHOST'], app.config['DATABASE'], app.config['DBUSER']))

# set up pony
db.bind(provider='postgres', host=app.config['DBHOST'],
        database=app.config['DATABASE'],
        user=app.config['DBUSER'],
        password=app.config['DBPWD'],
        sslmode=app.config['DBSSLMODE'])
db.generate_mapping()


def str_to_datetime(ans: str) -> Union[datetime, None]:
    if ans:
        d = datetime.strptime(ans, "%Y-%m-%d-%H-%M-%S")
        # no tz info, assumed to be in UTC
        return d
    return None


class VIServiceException(Exception):

    def __init__(self, message, status_code):
        Exception.__init__(self)
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


@app.errorhandler(VI401Exception)
def handle_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    response.headers = {'WWW-Authenticate': 'Bearer realm="access to VI backend"'}
    return response


@app.errorhandler(VIServiceException)
def handle_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.before_request
def before_request():
    # log actual full url of each call
    # saves having to correlate with uwsgi server logs
    logging.info("handling request to %s", request.url)


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
    user = User.get(email=email)
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
    user = None
    try:
        user = User[user_id]
    except ObjectNotFound:
        # not authenticated
        logging.error("check_user: failed to authenticate user id does not exist - %s", user_id)
        raise VI401Exception("Failed to authenticate user.")

    if user.role not in role_set:
        # no permission
        logging.warning("in check_user: insufficient privilege for user %s", user.email)
        raise VI403Exception("User does not have permission.")

    return user


# Define our callback function to check if a token has been revoked or not
@jwt.token_in_blacklist_loader
def check_if_token_revoked(decoded_token):
    return is_token_revoked(decoded_token)


# password recovery
@app.route('/reset-password-start', methods=['POST'])
@db_session
def reset_password_start():
    logging.info("in /reset-password-start[POST]")
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
    user = User.get(email=email)
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
@db_session
def reset_password_finish():
    logging.info("in /reset-password-finish[POST]")
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
    try:
        user = User[user_id]
    except ObjectNotFound:
        # not authenticated
        logging.error("reset password: User not found")
        raise VI404Exception("User not found.")
    logging.info("finishing reset of password for %s", user.email)
    user.pword = argon2.hash(password)
    for token in user.tokens:
        token.revoked = True
    return jsonify(
        {'count': 1, 'data': [{'type': 'Message', 'msg': "Successfully updated password for {}".format(user.email)}]})


# Standard login endpoint. Will return a fresh access token and
# a refresh token
@app.route('/login', methods=['POST'])
@db_session
def login():
    logging.info("in /login[POST]")
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    user = auth_user(email, password)
    logging.info("login: logging in %s", user.email)
    user.last_login = datetime.utcnow()
    # Store the tokens in our store with a status of not currently revoked.
    access_token = create_access_token(identity={'id': user.id}, fresh=True)
    refresh_token = create_refresh_token(identity={'id': user.id})

    add_token_to_database(access_token, user)
    add_token_to_database(refresh_token, user)
    # create_access_token supports an optional 'fresh' argument,
    # which marks the token as fresh or non-fresh accordingly.
    # As we just verified their email and password, we are
    # going to mark the token as fresh here.
    ret = {'count': 1, 'data': [{'type': 'AccessToken', 'access_token': access_token, 'refresh_token': refresh_token}]}
    return jsonify(ret)


# Refresh token endpoint. This will generate a new access token from
# the refresh token.
@app.route('/refresh', methods=['POST'])
@db_session
@jwt_refresh_token_required
def refresh():
    logging.info("in /refresh[POST]")
    user = check_user(('vivendor', 'viuser'))
    logging.info("refresh: refreshing %s", user.email)
    user.last_login = datetime.utcnow()
    new_token = create_access_token(identity={'id': user.id}, fresh=True)
    add_token_to_database(new_token, user)
    ret = {'count': 1, 'data': [{'type': 'AccessToken', 'access_token': new_token, 'refresh_token': None}]}
    return jsonify(ret)


# Endpoint for revoking all the current users tokens
@app.route('/logout', methods=['DELETE'])
@db_session
@jwt_required
def logout():
    logging.info("in /logout[DELETE]")
    user = check_user(('vivendor', 'viuser'))
    logging.info("logout: logging out %s", user.email)
    for token in user.tokens:
        token.revoked = True
    return jsonify(
        {'count': 1, 'data': [{'type': 'Message', 'msg': "Successfully logged out user {}".format(user.email)}]})


#
# user methods
#


# register a new user
# must have token
# must be vivendor to create viuser
@app.route('/users', methods=['POST'])
@db_session
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
        flush()
    except (IntegrityError, TransactionIntegrityError):
        # already exists
        logging.error("new_user: user name exists %s", email)
        raise VI400Exception("User with specified email already exists.")
    ret_results = {'count': 1, 'data': [UserView.render(user)]}

    return jsonify(ret_results), 201


# get user data
# fresh token required
# must be owner of data
@app.route('/users', methods=['GET'])
@db_session
@jwt_required
def get_user():
    logging.info("in /users[GET]")
    user = check_user(('viuser',))
    ret_results = {'count': 1, 'data': [UserView.render(user)]}
    return jsonify(ret_results)


# modify user data
@app.route('/users', methods=['PATCH'])
@db_session
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
            if User.exists(email=email):
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

    flush()

    ret_results = {'count': 1, 'data': [UserView.render(user)]}
    return jsonify(ret_results)


# delete user data
@app.route('/users', methods=['DELETE'])
@db_session
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
@app.route('/users/answers', methods=['GET'])
@db_session
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
        question = None
        try:
            question = Question[question_id]
        except ObjectNotFound:
            raise VI404Exception("No Question with the specified id was found.")
        answers = answers.filter(lambda a: a.question == question)

    idx = None
    try:
        # get index
        idx = Index[index_id]
    except ObjectNotFound:
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
@app.route('/users/answers', methods=['POST'])
@db_session
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

    idx = None
    try:
        # get index
        idx = Index[index_id]
    except ObjectNotFound:
        raise VI404Exception("No Index with the specified id was found.")

    # load the components
    idx.index_components.load()

    ret_answers = []
    for question_name in answers.keys():
        # validate answers here before saving
        # empty answers are not saved
        # all answers are strings so this tests for empty string or None
        if answers[question_name]:
            question = None
            try:
                question = Question[question_name]
            except ObjectNotFound:
                # warning - answer for question that does not exist
                raise VI404Exception("No Question with the specified id was found.")
            # load related sub components
            question.index_sub_components.load()

            # create Answer
            answer = Answer(question=question, time_received=trecv, answer=answers[question_name], user=user)
            ret_answers.append(answer)

    # flush to get ids assigned before rendering
    flush()

    ranswers = {'count': len(ret_answers), 'data': [AnswerView.render(a) for a in ret_answers]}
    return jsonify(ranswers), 201


# get answer statistics for user
@app.route('/users/answers/counts', methods=['GET'])
@db_session
@jwt_required
def answer_counts_for_user():
    logging.info("in /users/answers/counts[GET]")

    # authenticate user
    user = check_user(('viuser',))

    answers = user.answers

    idx = None
    try:
        # get index
        idx = Index[index_id]
    except ObjectNotFound:
        raise VI404Exception("No Index with the specified id was found.")
    answers = answers.filter(lambda a: idx in a.indexes)

    counts = {index_id: {'total': 0, 'answered': 0}}
    for c in idx.index_components:
        counts[c.name] = {'total': 0, 'answered': 0}
        for q in c.questions:
            counts[c.name]['total'] += 1
            counts[index_id]['total'] += 1
            qanswers = answers.filter(lambda a: a.question == q)
            if len(qanswers) > 0:
                counts[c.name]['answered'] += 1
                counts[index_id]['answered'] += 1

    ret_answers = {'count': 1, 'data': [counts]}
    return jsonify(ret_answers)


# get results for user
# filters as url parameters - as-of-time
@app.route('/users/results', methods=['GET'])
@db_session
@jwt_required
def results_for_user():
    logging.info("in /users/results[GET]")
    trecv = datetime.utcnow().replace(microsecond=0)

    # authenticate user
    user = check_user(('viuser',))
    results = user.results

    idx = None
    try:
        # get index
        idx = Index[index_id]
    except ObjectNotFound:
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
@app.route('/users/results', methods=['POST'])
@db_session
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

    idx = None
    try:
        # get index
        idx = Index[index_id]
    except ObjectNotFound:
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

    # flush to get ids assigned before rendering
    flush()
    rresults = {'count': 1, 'data': [ResultView.render(res)]}
    return jsonify(rresults), 201


#
# recommendation methods
#

@app.route('/users/recommendations/<component_name>', methods=['GET'])
@db_session
@jwt_required
def get_recommendations_for_result(component_name):
    logging.info("in /users/recommendations/%s[GET]", component_name)
    # authenticate user
    user = check_user(('viuser',))

    recommendations = []

    # get latest result
    result = None
    results = user.results

    idx = None
    try:
        # get index
        idx = Index[index_id]
    except ObjectNotFound:
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


#
# answer methods
#

# get answer
@app.route('/answers/<int:answer_id>', methods=['GET'])
@db_session
@jwt_required
def get_answer(answer_id):
    logging.info("in /answers/<answer_id>[GET]")
    user = check_user(('viuser',))
    answer = None
    try:
        answer = Answer[answer_id]
    except ObjectNotFound:
        # no answer with this id
        raise VI404Exception("No Answer with specified id.")

    if answer.user != user:
        # resource exists but is not owned by, and therefore not viewable by, user
        raise VI403Exception("User does not have permission.")

    ranswers = {'count': 1, 'data': [AnswerView.render(answer)]}
    return jsonify(ranswers)


# get results that used an answer
@app.route('/answers/<int:answer_id>/results', methods=['GET'])
@db_session
@jwt_required
def get_answer_results(answer_id):
    logging.info("in /answers/<answer_id>/results[GET]")
    user = check_user(('viuser',))
    answer = None
    try:
        answer = Answer[answer_id]
    except ObjectNotFound:
        # no answer with this id
        raise VI404Exception("No Answer with specified id.")

    if answer.user != user:
        # resource exists but is not owned by, and therefore not viewable by, user
        raise VI403Exception("User does not have permission.")

    rresults = {'count': len(answer.results), 'data': [ResultView.render(r) for r in answer.results]}
    return jsonify(rresults)


#
# result methods
#


# get result
@app.route('/results/<int:result_id>', methods=['GET'])
@db_session
@jwt_required
def get_result(result_id):
    logging.info("in /results/<result_id>[GET]")
    user = check_user(('viuser',))

    result = None
    try:
        result = Result[result_id]
    except ObjectNotFound:
        # no result with this id
        raise VI404Exception("No Result with specified id.")

    if result.user != user:
        # resource exists but is not owned by, and therefor enot viewable by, user
        raise VI403Exception("User does not have permission.")
    rresults = {'count': 1, 'data': [ResultView.render(result)]}
    return jsonify(rresults)


# get result component
@app.route('/results/<int:result_id>/components/<int:component_id>', methods=['GET'])
@db_session
@jwt_required
def get_result_component(result_id, component_id):
    logging.info("in /results/%s/components/%s[GET]", result_id, component_id)
    # authenticate user
    user = check_user(('viuser',))
    result = None
    try:
        result = Result[result_id]
    except ObjectNotFound:
        # no result with this id
        raise VI404Exception("No Result with specified id.")
    if result.user != user:
        # resource exists but is not owned by, and therefor enot viewable by, user
        raise VI403Exception("User does not have permission.")
    component = None
    try:
        component = ResultComponent[component_id]
    except ObjectNotFound:
        # Component does not exist
        raise VIServiceException(404, "no ResultComponent with specified id")
    if component.result != result:
        raise VIServiceException(404, "no ResultComponent with specified id in this resource tree")
    rresults = {'count': 1, 'data': [ResultComponentView.render(component)]}
    return jsonify(rresults)


# get answers that went into a result
@app.route('/results/<int:result_id>/answers', methods=['GET'])
@db_session
@jwt_required
def get_result_answers(result_id):
    logging.info("in /results/%s/answers[GET]", result_id)
    user = check_user(('viuser',))

    result = None
    try:
        result = Result[result_id]
    except ObjectNotFound:
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
@db_session
@jwt_required
def get_statistics():
    logging.info("in /statistics[GET]")
    trecv = datetime.utcnow()
    # authenticate user
    check_user(('viuser',))

    agerange = request.args.get('agerange')
    gender = request.args.get('gender')
    region = request.args.get('region')

    if agerange:
        if gender:
            # age range is string like "x-y"
            ages = agerange.split('-')
            dplus = date.today() - timedelta(days=int(ages[0]) * 365)
            dminus = date.today() - timedelta(days=int(ages[1]) * 365)
            # noinspection PyTypeChecker
            vgs = select((r.name, avg(r.points), avg(r.maxforanswered))
                         for r in Result for u in User
                         if r.user == u and u.gender == gender
                         and between(u.birth_date, dminus, dplus)
                         and r.time_generated == max(r2.time_generated for r2 in Result if r2.user == u))[:]
        else:
            # age range is string like "x-y"
            ages = agerange.split('-')
            dplus = date.today() - timedelta(days=int(ages[0]) * 365)
            dminus = date.today() - timedelta(days=int(ages[1]) * 365)
            # noinspection PyTypeChecker
            vgs = select((r.name, avg(r.points), avg(r.maxforanswered))
                         for r in Result for u in User
                         if r.user == u
                         and between(u.birth_date, dminus, dplus)
                         and r.time_generated == max(r2.time_generated for r2 in Result if r2.user == u))[:]
    else:
        if gender:
            # noinspection PyTypeChecker
            vgs = select((r.name, avg(r.points), avg(r.maxforanswered))
                         for r in Result for u in User
                         if r.user == u and u.gender == gender
                         and r.time_generated == max(r2.time_generated for r2 in Result if r2.user == u))[:]
        else:
            # noinspection PyTypeChecker
            vgs = select((r.name, avg(r.points), avg(r.maxforanswered))
                         for r in Result for u in User
                         if r.user == u
                         and r.time_generated == max(r2.time_generated for r2 in Result if r2.user == u))[:]

    if vgs:
        result = {
            'type': 'Result',
            'attributes': {
                'maxforanswered': vgs[0][2],
                'maxpoints': 1000,
                'name': 'Vitality Index',
                'points': vgs[0][1],
                'time_generated': trecv.strftime("%Y-%m-%d-%H-%M-%S"),
                'result_components': []
            }
        }

        if agerange:
            if gender:
                # age range is string like "x-y"
                ages = agerange.split('-')
                dplus = date.today() - timedelta(days=int(ages[0]) * 365)
                dminus = date.today() - timedelta(days=int(ages[1]) * 365)
                # noinspection PyTypeChecker
                vgs = select((r.name, avg(r.points), avg(r.maxforanswered))
                             for r in ResultComponent for u in User
                             if r.result.user == u and u.gender == gender
                             and between(u.birth_date, dminus, dplus)
                             and r.result.time_generated == max(r2.time_generated for r2 in Result if r2.user == u))[:]
            else:
                # age range is string like "x-y"
                ages = agerange.split('-')
                dplus = date.today() - timedelta(days=int(ages[0]) * 365)
                dminus = date.today() - timedelta(days=int(ages[1]) * 365)
                # noinspection PyTypeChecker
                vgs = select((r.name, avg(r.points), avg(r.maxforanswered))
                             for r in ResultComponent for u in User
                             if r.result.user == u
                             and between(u.birth_date, dminus, dplus)
                             and r.result.time_generated == max(r2.time_generated for r2 in Result if r2.user == u))[:]
        else:
            if gender:
                # noinspection PyTypeChecker
                vgs = select((r.name, avg(r.points), avg(r.maxforanswered))
                             for r in ResultComponent for u in User
                             if r.result.user == u and u.gender == gender
                             and r.result.time_generated == max(r2.time_generated for r2 in Result if r2.user == u))[:]
            else:
                # noinspection PyTypeChecker
                vgs = select((r.name, avg(r.points), avg(r.maxforanswered))
                             for r in ResultComponent for u in User
                             if r.result.user == u
                             and r.result.time_generated == max(r2.time_generated for r2 in Result if r2.user == u))[:]

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


if __name__ == '__main__':
    app.run(host=app.config['WWWHOST'],
            port=app.config['WWWPORT'])
