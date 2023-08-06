from eveapi2 import character_affiliation

from .conftest import xml


def test_character_affiliation():
    xml_data = xml('character_affiliation')

    result = character_affiliation(xml_data)
    char = list(result.characters)[0]

    assert char.character_id == 93227004
    assert char.name == "Lukas Nemec"
    assert char.corporation_name == "S0utherN Comfort"
    assert char.corporation_id == 458742701
    assert char.alliance_id == 99002938
    assert char.alliance_name == "DARKNESS."
    assert char.faction_id == 0
    assert char.faction_name == ""


def test_character_affiliation2():
    xml_data = xml('character_affiliation')

    result = character_affiliation(xml_data)
    char = list(result.characters)[1]

    assert char.character_id == 93389468
    assert char.name == "Lukas Davemec"
    assert char.corporation_name == "Royal Amarr Institute"
    assert char.corporation_id == 1000077
    assert char.alliance_id == 0
    assert char.alliance_name is None
    assert char.faction_id == 0
    assert char.faction_name == ""
