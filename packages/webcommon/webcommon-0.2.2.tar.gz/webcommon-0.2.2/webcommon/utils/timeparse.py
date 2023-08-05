# Copyright (C) 2014-2015, Availab.io(R) Ltd. All rights reserved.

import re
from datetime import timedelta


class TimeHelper():
    def __init__(self):
        """Constructor

        Args:

        Attributes:

        """
        pass

    @staticmethod
    def str_to_timedelta(time_str):
        """
        Parses string to timedelta object.

        String is formatted simply - number of time units followed by letter
        identifying the unit.

        Args:
            time_str: String containing time in specified format
        Returns:
            Timedelta object.
        Raises:
            ValueError exception if format is bad.
        """

        err_message = ("Wrong format of the time string '" + time_str +
                       "'. Example - 1w2d3h4m5s means 1 week, 2 days, 3 hours, "
                       "4 minutes and 5 seconds. Note that order is important, '5s1w' "
                       "is not valid as weeks may not precede seconds")

        regex = re.compile(
            r'^((?P<weeks>\d+?)w)?((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?$')
        parts = regex.search(time_str)
        if not parts:
            raise ValueError(err_message)

        parts = parts.groupdict()
        if len(filter(lambda x: parts[x] is not None, parts.keys())) == 0:
            raise ValueError(err_message)

        time_params = {}
        for (name, param) in parts.iteritems():
            if param:
                time_params[name] = int(param)
        return timedelta(**time_params)
