# Copyright (C) 2015, Availab.io(R) Ltd. All rights reserved.

from logging.handlers import RotatingFileHandler
from logging import Formatter
import traceback

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
        handler = RotatingFileHandler(AppLogger._app.config['LOG_FILE'], maxBytes=10737418240, backupCount=7) #10MB
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
    def log_exception_as_error():
        """Method to log an exception which is being handled right now
        Args:

        Returns:

        """
        AppLogger._app.logger.error(traceback.format_exc())

    @staticmethod
    def log_exception_as_warning():
        """Method to log an exception which is being handled right now
        Args:

        Returns:

        """
        AppLogger._app.logger.warning(traceback.format_exc())
