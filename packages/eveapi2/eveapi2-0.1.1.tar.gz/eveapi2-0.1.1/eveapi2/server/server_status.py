from ..models.server_status import ServerStatus
from ..response import Response
from ..utils import xml_input


@xml_input
def server_status(xml_data):
    """
    server_status(xml_string) -> Response obj

    Returns populated Response object. Under status attribute is a ServerStatus
    object populated from given xml_data.
    """
    response = Response(xml_data)
    response.status = ServerStatus(response._soup.result)
    return response


server_status.url = "https://api.eveonline.com/server/ServerStatus.xml.aspx"
