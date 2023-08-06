from bs4.element import Tag

from ..models.call import Call
from ..models.call_group import CallGroup
from ..response import Response
from ..utils import xml_input


def call_groups_generator(response_obj):
    rowset = response_obj._soup.select('rowset[name="callGroups"]')
    if len(rowset) == 1:
        for row in rowset[0].children:
            if isinstance(row, Tag):
                yield CallGroup(row)


def calls_generator(response_obj):
    rowset = response_obj._soup.select('rowset[name="calls"]')

    if len(rowset) == 1:
        for row in rowset[0].children:
            if isinstance(row, Tag):
                yield Call(row)


@xml_input
def call_list(xml_data):
    """
    call_list(xml_string) -> Response obj

    Returns populated Response object. Under call_groups attribute is generator
    with CallGroup objects. Under calls attribute is generator with Call
    objects.
    """
    response = Response(xml_data)
    response.call_groups = call_groups_generator(response)
    response.calls = calls_generator(response)
    return response


call_list.url = "https://api.eveonline.com/api/CallList.xml.aspx"
