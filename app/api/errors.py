from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES


def error_response(error, headers=None):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    if headers:

    return response


def bad_request(error):
    return error_response(400, message)

