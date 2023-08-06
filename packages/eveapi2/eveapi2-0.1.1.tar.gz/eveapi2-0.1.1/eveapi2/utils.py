from datetime import datetime
from functools import wraps

import pytz

from eveapi2 import DATETIME_FORMAT


def xml_input(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not isinstance(args[0], str):
            raise TypeError('XML data must be string.')

        return func(*args, **kwargs)

    return wrapper


def handle_boolean(value):
    if value == 'True':
        return True

    return False


def handle_int(value):
    if value:
        return int(value)


def handle_datetime(value):
    if value:
        return pytz.utc.localize(
            datetime.strptime(value, DATETIME_FORMAT)
        )
