# Copyright (C)2015, Availab.io(R) Ltd. All rights reserved.


class TestDispatcher:
    """
    Global dispatcher for classes which are needed to be mocked in tests.

    All such classes should be referenced from code only using dispatcher.
    Set the correct class objects at startup/
    """
    def __init__(self):
        pass

    def init(self, app, db):
        """
        Initializes the class

        Args:
            app: Flask instance
            db: SqlAlchemy instance
        """
        self.app = app
        self.db = db

test_dispatcher = TestDispatcher()