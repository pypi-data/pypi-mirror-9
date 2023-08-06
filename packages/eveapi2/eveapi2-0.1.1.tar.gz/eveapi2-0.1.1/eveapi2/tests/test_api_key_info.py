import datetime
import pytz

from eveapi2 import api_key_info

from .conftest import xml


def test_api_key_info():
    xml_data = xml('api_key_info')

    result = api_key_info(xml_data)
    d = pytz.utc.localize(
        datetime.datetime(2016, 3, 12, 17, 46, 14)
    )
    assert result.api_key_info.access_mask == "59244552"
    assert result.api_key_info.type == "Account"
    assert result.api_key_info.expires == d


def test_api_key_info_characters():
    xml_data = xml('api_key_info')

    result = api_key_info(xml_data)
    char = list(result.api_key_info.characters)[0]

    assert char.character_id == 93227004
    assert char.name == "Lukas Nemec"
