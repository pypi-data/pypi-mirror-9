from bs4.element import Tag

from ..models.character import Character
from ..response import Response
from ..utils import xml_input


# We cannot use characters_generator from account.characters because in this
# case some characters in the result may be empty.
def characters_generator(response_obj):
    for row in response_obj._soup.result.rowset.children:
        if isinstance(row, Tag) and row.get('name'):
            yield Character(row)


@xml_input
def character_id(xml_data):
    """
    character_id(xml_string) -> Response obj

    Returns populated Response object. Under account_status attribute is a
    generator with AccountStatus objects populated from given xml_data.
    """
    response = Response(xml_data)
    response.characters = characters_generator(response)
    return response


character_id.url = "https://api.eveonline.com/eve/CharacterID.xml.aspx"
