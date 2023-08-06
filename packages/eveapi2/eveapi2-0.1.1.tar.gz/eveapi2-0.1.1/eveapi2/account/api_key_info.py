from ..models.api_key_info import APIKeyInfo
from ..response import Response
from ..utils import xml_input


@xml_input
def api_key_info(xml_data):
    """
    api_key_info(xml_string) -> Response obj

    Returns populated Response object. Under api_key_info attribute is a
    APIKeyInfo object populated from given xml_data.
    """
    response = Response(xml_data)
    response.api_key_info = APIKeyInfo(response._soup.result.key)
    return response


api_key_info.url = "https://api.eveonline.com/account/APIKeyInfo.xml.aspx"
