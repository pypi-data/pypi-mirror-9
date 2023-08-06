DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIMEZONE = 'UTC'

VERSION = '0.1.1'

from .exceptions import APIError

from .account.account_status import account_status
from .account.api_key_info import api_key_info
from .account.characters import characters
from .api.call_list import call_list
from .eve.alliance_list import alliance_list
from .eve.character_affiliation import character_affiliation
from .eve.character_id import character_id
from .server.server_status import server_status
