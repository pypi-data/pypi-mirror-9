from flask import jsonify
from werkzeug.exceptions import HTTPException


def make_json_error(ex):
    response = jsonify(message=str(ex))
    if isinstance(ex, HTTPException):
        response.status_code = ex.code
    else:
        response.status_code = 500
    return response
