from bs4.element import Tag

from ..models.character import Character
from ..response import Response
from ..utils import xml_input


def characters_generator(response_obj):
    for row in response_obj._soup.result.rowset.children:
        if isinstance(row, Tag):
            yield Character(row)


@xml_input
def characters(xml_data):
    """
    character(xml_string) -> Response obj

    Returns populated Response object. Under account_status attribute is a
    generator populated with Character objects from given xml_data.
    """
    response = Response(xml_data)
    response.characters = characters_generator(response)
    return response


characters.url = "https://api.eveonline.com/account/characters.xml.aspx"
