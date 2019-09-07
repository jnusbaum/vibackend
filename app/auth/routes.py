import logging
from datetime import datetime
from passlib.hash import argon2
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask import request, jsonify
from flask_jwt_extended import (
    jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token
)
from app.auth import bp
from app.api.errors import VI400Exception, VI401Exception, VI500Exception, VI404Exception
from app.auth.auth import auth_user, check_user, add_token_to_database
from app import db
from vidb.models import User
from vimailserver import mail_tasks


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
    user = User.query.filter(email=email).one_or_none()
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
    user = User.query.get(user_id)
    if not user:
        # not authenticated
        logging.error("reset password: User not found")
        raise VI404Exception("User not found.")
    logging.info("finishing reset of password for %s", user.email)
    user.pword = argon2.hash(password)
    for token in user.tokens:
        token.revoked = True
        db.session.add(token)
    db.session.commit()
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
