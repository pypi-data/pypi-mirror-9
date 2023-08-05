# Copyright (C) 2015, Availab.io(R) Ltd. All rights reserved.
import unittest
from webcommon.test.avio_api_test_case_helper import AvioApiTestCaseHelper
from webcommon.test.test_dispatcher import test_dispatcher


class AvioApiTestCase(unittest.TestCase, AvioApiTestCaseHelper):
    """
    Base class for testing flask API requests
    """
    def setUp(self):
        self.app = test_dispatcher.app
        self.client = self.app.test_client(use_cookies=True)

        test_dispatcher.db.session.remove()
        test_dispatcher.db.drop_all(app=test_dispatcher.app)
        test_dispatcher.db.create_all(app=test_dispatcher.app)

    def tearDown(self):
        pass
