import logging

from . import LoggerConfig


def configure_logging():
    """
    Configure the logging system using a LoggerConfig instance.
    """

    logger_config = LoggerConfig()

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    logger.addHandler(logger_config.create_file_handler())
    logger.addHandler(logger_config.create_console_handler())