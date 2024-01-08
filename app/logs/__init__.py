from functools import wraps
from flask import request, current_app
import logging


def configure_logging():
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename="app/logs/app.log",
    )


def log_request_headers_information(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_app.logger.info(f"Request Headers: {request.headers}")
        if request.data:
            current_app.logger.info(f"Request Body: {request.get_json()}")
        return f(*args, **kwargs)
    return decorated_function

def log_request_body_information(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.data:
            current_app.logger.info(f"Request Body: {request.get_json()}")
        return f(*args, **kwargs)
    return decorated_function