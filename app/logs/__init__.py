from functools import wraps
from flask import request, current_app
import logging
from logging.handlers import TimedRotatingFileHandler


def configure_logging():
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    file_handler = TimedRotatingFileHandler(
        'app/logs/api.log', 
        when="D", 
        interval=1, 
        backupCount=1
    )
    file_handler.setFormatter(logging.Formatter(
        fmt=log_format, 
        datefmt=date_format
    ))

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        fmt=log_format, 
        datefmt=date_format
    ))

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


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