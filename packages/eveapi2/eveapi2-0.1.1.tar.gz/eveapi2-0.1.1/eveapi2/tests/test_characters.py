from eveapi2 import characters

from .conftest import xml


def test_characters():
    xml_data = xml('characters')

    result = characters(xml_data)
    char = list(result.characters)[0]

    assert char.character_id == 93227004
    assert char.name == "Lukas Nemec"
    assert char.corporation_name == "S0utherN Comfort"
    assert char.corporation_id == 458742701
    assert char.alliance_id == 99002938
    assert char.alliance_name == "DARKNESS."
    assert char.faction_id == 0
    assert char.faction_name == ""
