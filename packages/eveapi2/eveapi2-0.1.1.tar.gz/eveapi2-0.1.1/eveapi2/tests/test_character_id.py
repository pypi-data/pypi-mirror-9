from eveapi2 import character_id

from .conftest import xml


def test_character_id():
    xml_data = xml('character_id')

    result = character_id(xml_data)
    char = list(result.characters)[0]

    assert char.character_id == 93227004
    assert char.name == "Lukas Nemec"


def test_character_id2():
    xml_data = xml('character_id')

    result = character_id(xml_data)
    char = list(result.characters)[1]

    assert char.character_id == 93526243
    assert char.name == "Lukas Nemec1"
