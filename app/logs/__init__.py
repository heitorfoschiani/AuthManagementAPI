from functools import wraps
from flask import request, current_app
import logging


def configure_logging():
    current_app.logger.basicConfig(
        level=current_app.logger.WARNING,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename="app/logs/app.log",
    )


def log_request_information(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_app.logger.info(f"Request Headers: {request.headers}")
        if request.data:
            current_app.logger.info(f"Request Body: {request.get_json()}")
        return f(*args, **kwargs)
    return decorated_function