import datetime
import pytz
import pytest

from eveapi2 import APIError
from eveapi2.response import Response

from .conftest import xml


def test_response():
    xml_data = xml('response')
    r = Response(xml_data)

    current_time = pytz.utc.localize(datetime.datetime(2015, 3, 8, 10, 9, 36))
    cached_until = pytz.utc.localize(datetime.datetime(2015, 3, 8, 16, 6, 36))

    assert r.current_time == current_time
    assert r.cached_until == cached_until

    # Please note that this test may not pass if your system time is wrong.
    assert r.is_refreshable is True


def test_raises():
    xml_data = xml('error')

    with pytest.raises(APIError):
        Response(xml_data)
