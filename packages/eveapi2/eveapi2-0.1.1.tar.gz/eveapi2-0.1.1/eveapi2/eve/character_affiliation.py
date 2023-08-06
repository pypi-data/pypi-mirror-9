from ..account.characters import characters_generator
from ..response import Response
from ..utils import xml_input


@xml_input
def character_affiliation(xml_data):
    """
    character_afiiliation(xml_string) -> Response obj

    Returns populated Response object. Under characters attribute is a generator
    with Character objects populated from given xml_data.
    """
    response = Response(xml_data)
    response.characters = characters_generator(response)
    return response


character_affiliation.url = "https://api.eveonline.com/eve/CharacterAffiliation.xml.aspx"
