import logging
from logging import FileHandler
import os


class LoggerConfig:
    def __init__(self):
        self.log_file = "app/logs/files/api.log"
        self.log_format = "%(asctime)s - %(levelname)s - %(message)s"
        self.date_format = "%Y-%m-%d %H:%M:%S"
        self.ensure_log_directory_exists()

    def ensure_log_directory_exists(self):
        """
        Ensure that the directory for the log file exists.
        If it doesn't, create it.
        """
        log_dir = os.path.dirname(self.log_file)
        os.makedirs(log_dir, exist_ok=True)

    def create_file_handler(self):
        """
        Create and configure the file handler.
        """

        file_handler = FileHandler(self.log_file)
        file_handler.setFormatter(self.create_formatter())

        return file_handler

    def create_console_handler(self):
        """
        Create and configure the console handler.
        """

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.create_formatter())

        return console_handler
    
    def create_formatter(self):
        """
        Create a logging formatter.
        """

        logging_formatter = logging.Formatter(
            fmt=self.log_format, 
            datefmt=self.date_format
        )

        return logging_formatter