# Copyright (C) 2014-2015, Availab.io(R) Ltd. All rights reserved.

"""
    JSON helper response methods
"""

from flask import Response, json


def json_ok(message=None, status_code=200, data=None):
    """Ok message

    Args:
      message: message to be sent
      status_code: HTTP status code to be sent
      data: data to be sent

    Returns:
      response object
    """
    to_serialize = {'status': 'success', 'message': message, 'data': data}

    json_data = json.dumps(to_serialize)
    rsp = Response(json_data, status=status_code)
    return rsp


def json_failed(message="There was an error during processing the request", status_code=400, data=None, ):
    """Fail message

    Args:
      message: message to be sent
      status_code: HTTP status code to be sent
      data: data to be sent

    Returns:
      response object

    """

    to_serialize = {'status': 'failed', 'message': message, 'data': data}
    json_data = json.dumps(to_serialize)
    rsp = Response(json_data, status=status_code)
    return rsp
