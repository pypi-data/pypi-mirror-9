# Copyright (C) 2014-2015, Availab.io(R) Ltd. All rights reserved.

from functools import wraps
from sqlalchemy.exc import DataError, IntegrityError, DBAPIError, \
    DisconnectionError, TimeoutError, SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from webcommon.json.json_response import json_failed
from webcommon.logging.app_logger import AppLogger


class AppException(Exception):
    """Base application exception class
       All other application specific should inherit from this class

    Args:

    Attributes:

    """

    def __init__(self, message):
        """Constructor

        Args:
          message: exception message

          Returns:

        """
        self.message = message


class AppResourceException(AppException):
    """Application resource exception class

    Args:

    Attributes:

    """

    def __init__(self, message, status_code, data=None):
        """Constructor

        Args:
          message: exception message
          status_code: resource status (HTTP) code
          date: data of the resource

        Returns:

        """
        super(AppResourceException, self).__init__(message)
        self.status_code = status_code
        self.data = data


class InternalException(AppResourceException):
    """
    Raised when something's wrong on APIs side (database down,
    timeout).

    Message should be human readable, but should contain no sensitive
    information, these can be stored in 'internal' for logging when
    exception is catched. Status code should be 5XX indicating server
    problem and if user should try it once more after some time or it
    is simply hopeless.
    """

    def __init__(self, message, status_code=500, data=None, internal=''):
        """
        Creates InternalException

        Args:
            message - human readable definition of what went wrong
            data - additional data (json) that can be shown to user
            status_code - HTTP status code that can be returned from resource
            internal - internal information
        """
        super(InternalException, self).__init__(message, status_code, data)
        self.internal = internal


class UserFaultException(AppResourceException):
    """
    Raised when action cannot be finished because user has made some
    error/mistake.

    Message should be human readable and it should tell user what went wrong
    and if possible how to fix it. Status code should be 4XX indicating wrong
    request. Data may contain additional data for message.
    """

    def __init__(self, message, status_code=400, data=None):
        """
        Creates UserFaultException

        Args:
            message - human readable definition of what went wrong
            data - additional data (json) that can be shown to user
        status_code - HTTP status code that can be returned from resource
        """
        super(UserFaultException, self).__init__(message, status_code, data)


def handle_common_exceptions(f):
    """
    Decorator for resource handlers to catch all AvailabioResourceExceptions
    which may be raised inside and return them as a json_failed responses

    Handles all SQLAlchemy exceptions, AvaialabioResourceException

    Args:
        f - function to be wrapped

    TODO: In future it should log all internal errors.
        """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)

        # Postgres user fault errors
        except (DataError, IntegrityError) as e:
            AppLogger.log_exception_as_warning(e, e.message)
            return json_failed(
                'Wrong request, see data for details',
                status_code=400,
                data=str(e.orig.pgerror)
            )
        # All other Postgres error are treated as internals errors
        except DBAPIError as e:
            AppLogger.log_exception_as_error(e, e.orig.pgerror)
            return json_failed(
                'An internal error occurred during processing your request.',
                status_code=500,
            )
        # SQL Alchemy exceptions
        except DisconnectionError as e:
            AppLogger.log_exception_as_error(e, e.message)
            return json_failed(
                'Underlying backend server is now disconnected due to regular maintenance. Please try it again later.',
                status_code=503,
            )  # TODO Wakeup everybody
        except TimeoutError as e:
            return json_failed(
                'Operation timed out. It seems that backend server is too busy right now, try it again later.',
                status_code=503,
            )
        # SQLAlchemy orm - you can handle it by yourself, if you don't
        # generic messages will be generated
        except NoResultFound as e:
            AppLogger.log_exception_as_error(e, e.message)
            return json_failed(
                'The requested object has not been found or you do not have sufficient rights to access it.',
                status_code=404,
            )
        except MultipleResultsFound as e:
            AppLogger.log_exception_as_error(e, e.message)
            return json_failed(
                'An internal error occurred during processing your request.',
                status_code=500,
            )
        except AppResourceException as e:
            AppLogger.log_exception_as_error(e, e.message)
            return json_failed(message=e.message, data=e.data, status_code=e.status_code)
        # Everything other...
        except (SQLAlchemyError, Exception) as e:
            AppLogger.log_exception_as_error(e, e.message)
            return json_failed(
                'An internal error occurred during processing your request.',
                status_code=500,
            )

    return decorated_function