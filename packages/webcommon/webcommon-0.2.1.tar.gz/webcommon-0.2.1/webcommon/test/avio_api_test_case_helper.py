# Copyright (C) 2015, Availab.io(R) Ltd. All rights reserved.
import json
from jsonschema import validate, ValidationError
from webcommon.utils.consts import Consts


class AvioApiTestCaseHelper:
    """
    Helper class for testing Flask API request-response
    """
    def api_request_check(self, end_point, expected_return_code, test_descr, method=Consts.HTTP_GET,
                          content_type=Consts.MIME_TYPE_APP_JSON, data=None, response_schema=None):
        """
        Request validation method

        Args:
            end_point: endpoint address
            expected_return_code: expected return code
            test_descr: description
            method: HTTP method, default 'GET'
            content_type: content type, default 'application/json'
            data: data to be sent
            response_schema: expected response schema

        Returns:
            response
        """

        request_method = None
        if method == Consts.HTTP_GET:
            request_method = self.client.get
        elif method == Consts.HTTP_POST:
            request_method = self.client.post
        elif method == Consts.HTTP_PUT:
            request_method = self.client.put
        elif method == Consts.HTTP_DELETE:
            request_method = self.client.delete
        else:
            raise (Exception("Requested method " + method + " is not known to client"))

        response = request_method(end_point,
                                  data=json.dumps(data),
                                  content_type=content_type)

        self.assertEqual(expected_return_code, response.status_code,
                         test_descr + " should return " + str(expected_return_code) +
                         " but returns " + str(response.status_code) + "\NMessage " +
                         str(response) + "\nData:" + str(response.data))

        if response_schema:
            if response.data is None or response.data == "":
                self.fail(test_descr + " - response contains no data, could not be validated")

            try:
                validate(json.loads(response.data), response_schema)
            except ValidationError as e:
                self.fail(test_descr + " -  validation of returned structure failed :\n" + e.message
                          + "\nValidated structure:\n" + response.data)

        return response
