# Copyright (C) 2015, Availab.io(R) Ltd. All rights reserved.
import json


class JsonSerializer:
    """
    Class for object serialization
    """

    def __init__(self):
        """Constructor

        Args:

        Returns:

        """
        pass

    @staticmethod
    def serialize(obj):
        """Method to serialize object to the JSON

        Args:
          obj: object to be serialized

        Returns:
          JSON string

        """
        return json.dumps(obj, default=lambda o: o.__dict__)