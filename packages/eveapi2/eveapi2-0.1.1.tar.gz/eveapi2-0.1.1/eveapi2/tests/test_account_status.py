import datetime
import pytz

from eveapi2 import account_status

from .conftest import xml


def test_account_status():
    xml_data = xml('account_status')

    paid_until = pytz.utc.localize(datetime.datetime(2015, 3, 31, 16, 57, 41))
    create_date = pytz.utc.localize(datetime.datetime(2013, 4, 15, 17, 37, 39))

    result = account_status(xml_data)
    assert result.account_status.logon_count == 821
    assert result.account_status.logon_minutes == 67407
    assert result.account_status.paid_until == paid_until
    assert result.account_status.create_date == create_date
