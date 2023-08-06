from bs4.element import Tag

from ..models.alliance import Alliance
from ..response import Response
from ..utils import xml_input


def alliance_generator(response_obj):
    rowset = response_obj._soup.result.rowset

    for row in rowset.children:
        if isinstance(row, Tag):
            yield Alliance(row)


@xml_input
def alliance_list(xml_data):
    """
    alliance_list(xml_string) -> Response obj

    Returns populated Response object. Under alliances attribute is a generator
    of Alliance objects populated from given xml_data.
    """
    response = Response(xml_data)
    response.alliances = alliance_generator(response)
    return response


alliance_list.url = "https://api.eveonline.com/eve/AllianceList.xml.aspx"
