# Copyright (C) 2015, Availab.io(R) Ltd. All rights reserved.

from threading import Thread

def async(f):
    """
    Helper attribute for async execution

    Args:
        f: function

    Returns:
        wrapper function
    """
    def wrapper(*args, **kwargs):
        """
        Wrapper async function

        Args:
            args: arguments
            kwargs: additional arguments
        """
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper
