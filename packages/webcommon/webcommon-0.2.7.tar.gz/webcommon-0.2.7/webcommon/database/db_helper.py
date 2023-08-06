# Copyright (C) 2014-2015, Availab.io(R) Ltd. All rights reserved.


class DbHelper():
    """
    Helper class for DB stuff
    """

    _db = None

    def __init__(self, db):
        """Class constructor

        Args:
          db: db instance, e.g. SqlAlchemy

         Returns:
        """
        self._db = db
        pass

    def add_and_do_commit(self, *objects):
        """Method to add items into db and commit the action

        Args:
          db: db instance, e.g. SqlAlchemy

         Returns:
        """
        if len(objects) != 0:
            self._db.session.add_all(objects)
        self._db.session.commit()

    def delete_and_do_commit(self, *objects):
        """ Method to delete items from db and commit action

        Args:
          db: db instance, e.g. SqlAlchemy

         Returns:
        """
        if len(objects) != 0:
            for obj in objects:
                self._db.session.delete(obj)
        self._db.session.commit()
