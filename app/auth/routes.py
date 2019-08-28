import logging
import datetime
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask import request, jsonify
from flask_jwt_extended import (
    jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    decode_token
)
from app.auth import bp
from app.errors.handlers import VI400Exception, VI401Exception, VI500Exception, VI404Exception
from app.auth.auth import auth_user, check_user


def _epoch_utc_to_datetime(epoch_utc) -> datetime:
    """
    Helper function for converting epoch timestamps (as stored in JWTs) into
    python datetime objects (which are easier to use with sqlalchemy).
    """
    return datetime.datetime.fromtimestamp(epoch_utc, tz=datetime.timezone.utc)


def add_token_to_database(encoded_token, user: User) -> None:
    """
    Adds a new token to the database. It is not revoked when it is added.
    """
    decoded_token = decode_token(encoded_token)
    jti = decoded_token['jti']
    token_type = decoded_token['type']
    expires = _epoch_utc_to_datetime(decoded_token['exp'])
    revoked = False

    Token(jti=jti,
          token_type=token_type,
          user=user,
          expires=expires,
          revoked=revoked
          )


def is_token_revoked(decoded_token) -> bool:
    """
    Checks if the given token is revoked or not. Because we are adding all the
    tokens that we create into this database, if the token is not present
    in the database we are going to consider it revoked, as we don't know where
    it was created.
    """
    jti = decoded_token['jti']
    token = Token.get(jti=jti)
    if token:
        return token.revoked
    else:
        return True


# password recovery
@bp.route('/reset-password-start', methods=['POST'])
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
    s = URLSafeTimedSerializer(bp.config['IDANGEROUSKEY'])
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
@bp.route('/reset-password-finish', methods=['POST'])
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
    s = URLSafeTimedSerializer(bp.config['IDANGEROUSKEY'])
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
@bp.route('/login', methods=['POST'])
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
@bp.route('/refresh', methods=['POST'])
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
@bp.route('/logout', methods=['DELETE'])
@jwt_required
def logout():
    logging.info("in /logout[DELETE]")
    user = check_user(('vivendor', 'viuser'))
    logging.info("logout: logging out %s", user.email)
    for token in user.tokens:
        token.revoked = True
    return jsonify(
        {'count': 1, 'data': [{'type': 'Message', 'msg': "Successfully logged out user {}".format(user.email)}]})
