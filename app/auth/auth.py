import logging
from passlib.hash import argon2
from typing import Tuple
from flask_jwt_extended import get_jwt_identity
from app.errors.handlers import VI401Exception, VI403Exception
from app.models import User

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
    user = User.query.filter_by(email=email)
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
    user = User.query.get(user_id)
    if not user:
        # not authenticated
        logging.error("check_user: failed to authenticate user id does not exist - %s", user_id)
        raise VI401Exception("Failed to authenticate user.")

    if user.role not in role_set:
        # no permission
        logging.warning("in check_user: insufficient privilege for user %s", user.email)
        raise VI403Exception("User does not have permission.")

    return user
