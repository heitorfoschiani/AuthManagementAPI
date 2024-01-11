from flask import request, current_app
import logging
from logging.handlers import TimedRotatingFileHandler
from functools import wraps

def configure_logging():
    handler = TimedRotatingFileHandler(
        'app/logs/api.log', 
        when="D", 
        interval=1, 
        backupCount=7  # Keep 7 days of logs
    )
    handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)


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