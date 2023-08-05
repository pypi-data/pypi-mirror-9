# Copyright (C) 2015, Availab.io(R) Ltd. All rights reserved.
import unittest
from webcommon.test.test_dispatcher import test_dispatcher


class AvioDbModelTestCase(unittest.TestCase):
    """
    Helper DB layer base class
    """
    def setUp(self):
        self.app = test_dispatcher.app
        # Remove session in case of tests produced some naughty invalid statements
        test_dispatcher.db.session.remove()
        test_dispatcher.db.drop_all(app=self.app)
        test_dispatcher.db.create_all(app=self.app)

    def tearDown(self):
        pass
