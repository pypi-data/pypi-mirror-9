import datetime
import pytz

from eveapi2 import alliance_list

from .conftest import xml


def test_aliance_list():
    xml_data = xml('alliance_list')
    assert alliance_list.url == "https://api.eveonline.com/eve/AllianceList.xml.aspx"

    result = alliance_list(xml_data)
    assert len(list(result.alliances)) == 3087


def test_alliance_dict():
    xml_data = xml('alliance_list')
    result = alliance_list(xml_data)
    alliance = list(result.alliances)[0]

    alliance_dict = {
        'alliance_id': 99003214,
        'executor_corp_id': 98199293,
        'member_count': 15940,
        'name': 'Brave Collective',
        'short_name': 'BRAVE',
        'start_date': pytz.utc.localize(
            datetime.datetime(2013, 5, 6, 22, 20, 14)
        )
    }

    result_dict = dict(alliance)
    del(result_dict['member_corporations'])

    assert result_dict == alliance_dict
