import logging
from datetime import datetime, timezone
from passlib.hash import argon2
from typing import Tuple
from flask_jwt_extended import get_jwt_identity, decode_token
from app.api.errors import VI401Exception, VI403Exception
from vidb.models import User, Token
from app import db, jwt


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
    token = Token.query.get(jti=jti)
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
    user = User.query.one_or_none(email=email).first()
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


# Define our callback function to check if a token has been revoked or not
@jwt.token_in_blacklist_loader
def check_if_token_revoked(decoded_token):
    return is_token_revoked(decoded_token)