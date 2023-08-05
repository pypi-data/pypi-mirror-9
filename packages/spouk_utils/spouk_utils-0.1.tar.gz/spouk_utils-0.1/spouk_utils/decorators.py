#!/usr/local/bin/python
# coding: utf-8
__author__ = 'spouk'

from functools import wraps


def debug_wrapper(exception_name=(BaseException, Exception), message='debug mode on [{}] [{}]', debug=False):
    """debug wrapper for functions"""

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
                return result
            except exception_name as error:
                if debug:
                    print message.format(f.__name__, kwargs), error
                return False

        return wrapper

    return decorator



