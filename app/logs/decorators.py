from functools import wraps
from flask import request, current_app


def log_request_headers_information(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_app.logger.info(f"Request Headers: {request.headers}")
        return f(*args, **kwargs)
    return decorated_function


def log_request_body_information(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.data:
            current_app.logger.info(f"Request Body: {request.get_json()}")
        return f(*args, **kwargs)
    return decorated_function