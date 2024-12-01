import logging
from logging.handlers import TimedRotatingFileHandler
import os


class LoggerConfig:
    def __init__(self):
        self.log_file = os.path.join("app/logs/files", "api.log")
        self.backup_directory = os.path.join("app/logs/files", "Backup")
        self.log_format = "%(asctime)s - %(levelname)s - %(message)s"
        self.date_format = "%Y-%m-%d %H:%M:%S"

    def create_formatter(self):
        """
        Create a logging formatter.
        """

        logging_formatter = logging.Formatter(
            fmt=self.log_format, 
            datefmt=self.date_format
        )

        return logging_formatter

    def create_file_handler(self):
        """
        Create and configure the file handler.
        """

        file_handler = TimedRotatingFileHandler(
            self.log_file,
            when="midnight",
            interval=1,
            backupCount=0
        )
        
        file_handler.namer = lambda name: os.path.join(
            self.backup_directory,
            f"api_{os.path.basename(name).split('.')[1]}.log"
        )
        file_handler.setFormatter(self.create_formatter())

        return file_handler

    def create_console_handler(self):
        """
        Create and configure the console handler.
        """

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.create_formatter())

        return console_handler


