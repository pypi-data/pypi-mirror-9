from ..models.account_status import AccountStatus
from ..response import Response
from ..utils import xml_input


@xml_input
def account_status(xml_data):
    """
    account_status(xml_string) -> Response obj

    Returns populated Response object. Under account_status attribute is a
    AccountStatus object populated from given xml_data.
    """
    response = Response(xml_data)
    response.account_status = AccountStatus(response._soup.result)
    return response


account_status.url = "https://api.eveonline.com/account/AccountStatus.xml.aspx"
