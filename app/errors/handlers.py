from app import db
from app.errors import bp
from app.api.errors import error_response as api_error_response


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


@bp.errorhandler(VI401Exception)
def handle_exception_401(error):
    return api_error_response(error, {'WWW-Authenticate': 'Bearer realm="access to VI backend"'})


@bp.errorhandler(VIServiceException)
def handle_exception(error):
    db.session.rollback()
    return api_error_response(error)

