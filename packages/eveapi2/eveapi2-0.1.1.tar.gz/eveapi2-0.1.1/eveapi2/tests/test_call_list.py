from eveapi2 import call_list

from .conftest import xml


def test_call_list():
    xml_data = xml('call_list')
    assert call_list.url == "https://api.eveonline.com/api/CallList.xml.aspx"

    result = call_list(xml_data)
    assert len(list(result.call_groups)) == 7
    assert len(list(result.calls)) == 54
