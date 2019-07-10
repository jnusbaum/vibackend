from vidb import *
from flask_jwt_extended import decode_token
from datetime import timezone


def _epoch_utc_to_datetime(epoch_utc):
    """
    Helper function for converting epoch timestamps (as stored in JWTs) into
    python datetime objects (which are easier to use with sqlalchemy).
    """
    return datetime.fromtimestamp(epoch_utc, tz=timezone.utc)


def add_token_to_database(encoded_token, user):
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


def is_token_revoked(decoded_token):
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
