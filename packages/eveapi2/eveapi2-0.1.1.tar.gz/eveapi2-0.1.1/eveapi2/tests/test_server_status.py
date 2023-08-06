import eveapi2

from .conftest import xml


def test_server_status():
    xml_data = xml('server_status')
    r = eveapi2.server_status(xml_data)

    assert r.status.server_open is True
    assert r.status.online_players == 26599
