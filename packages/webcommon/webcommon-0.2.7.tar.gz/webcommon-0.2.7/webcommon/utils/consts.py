# Copyright (C) 2015, Availab.io(R) Ltd. All rights reserved.


class Consts:
    """Class containing constants used multiple times in the application

    Args:

    Attributes:

    """
    def __init__(self):
        """Class constructor

        Args:

         Returns:
        """
        pass

    HTTP_CODE_OK = 200
    HTTP_CODE_CREATED = 201
    HTTP_CODE_ACCEPTED = 202
    HTTP_CODE_BAD_REQUEST = 400
    HTTP_CODE_UNAUTHORIZED = 401
    HTTP_CODE_FORBIDDEN = 403
    HTTP_CODE_NOT_FOUND = 404
    HTTP_CODE_INTERNAL_SERVER_ERROR = 500
    HTTP_CODE_SERVICE_UNAVAILABLE = 503
    
    MIME_TYPE_APP_JSON = 'application/json'
    HTTP_GET = 'get'
    HTTP_POST = 'post'
    HTTP_PUT = 'put'
    HTTP_PATCH = 'patch'
    HTTP_DELETE = 'delete'