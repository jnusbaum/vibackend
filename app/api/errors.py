from flask import jsonify


def error_response(error, headers=None):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    if headers:
        response.headers = headers
    return response


