# Copyright (C) 2015, Availab.io(R) Ltd. All rights reserved.

from logging.handlers import RotatingFileHandler
from logging import Formatter


class AppLogger:
    """
    Application logger
    It uses Flask build-in logging mechanism Flask.app.logger.*

    Examples:
      AppLogger.setup_logger(app) # app is the Flask instance

    """

    def __init__(self):
        """Constructor

        Args:

        Returns:

        """
        pass

    _app = None

    @staticmethod
    def setup_logger(application):
        """Logger setup method

        Args:

        Returns:

        """
        AppLogger._app = application
        handler = RotatingFileHandler(AppLogger._app.config['LOG_FILE'], maxBytes=10000, backupCount=7)
        handler.setLevel(AppLogger._app.config['LOG_LEVEL'])
        handler.setFormatter(Formatter(
            '%(asctime)s | %(levelname)s | %(message)s '))
        AppLogger._app.logger.addHandler(handler)

    @staticmethod
    def log_info(message):
        """Method for logging info

        Args:

        Returns:

        """
        AppLogger._app.logger.info(message)

    @staticmethod
    def log_warning(message):
        """Method for logging warning

        Args:

        Returns:

        """
        AppLogger._app.logger.warning(message)

    @staticmethod
    def log_error(message):
        """Method for logging error

        Args:

        Returns:

        """
        AppLogger._app.logger.error(message)

    @staticmethod
    def format_exception(exception, exception_content):
        """Method to format exception record

        Args:
          exception: exception name string
          exception_content: exception message
        Returns:
          formatted exception string
        """
        return "{0} : {1}".format(exception, exception_content)

    @staticmethod
    def log_exception_as_error(exception, exception_content):
        """Method to log an exception as an error message

        Args:
          exception: exception instance to get its type
          exception_content: exception message
        Returns:

        """
        AppLogger._app.logger.error(AppLogger.format_exception(type(exception), exception_content))

    @staticmethod
    def log_exception_as_warning(exception, exception_content):
        """Method to log an exception as a warning message

        Args:
          exception: exception instance to get its type
          exception_content: exception message
        Returns:

        """
        AppLogger._app.logger.warning(AppLogger.format_exception(type(exception), exception_content))
