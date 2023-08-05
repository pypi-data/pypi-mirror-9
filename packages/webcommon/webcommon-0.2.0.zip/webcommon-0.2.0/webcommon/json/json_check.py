# Copyright (C) 2014-2015, Availab.io(R) Ltd. All rights reserved.
from flask import request
from functools import wraps
from json_response import json_failed
from jsonschema import validate, ValidationError


def validate_json_request(schema, only_json=True):
    """Used as wrapper for request handlers. It validates
    the request against provided schema. Optionally checks
    valid content type"""

    def wraped(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            is_json = str(request.mimetype).lower() == 'application/json'

            if only_json and not is_json:
                return json_failed(status_code=415, message='Only application/json supported')

            if is_json:
                data = request.get_json()
                try:
                    validate(data, schema)

                except ValidationError as e:
                    return json_failed(message="Wrong input structure",
                                       status_code=400,
                                       data={
                                           "validated_against": schema,
                                           "error_mesage": e.message,
                                       }
                    )

            return f(*args, **kwargs)

        return decorated_function

    return wraped
