from datetime import datetime

from bs4 import BeautifulSoup
import pytz

from eveapi2 import DATETIME_FORMAT

from .exceptions import APIError


class Response:

    def __init__(self, xml_response):
        self._soup = BeautifulSoup(xml_response, 'lxml')
        self.check_errors()

    def check_errors(self):
        err = self._soup.error
        if err:
            raise APIError(err)

    @property
    def current_time(self):
        current_time = self._soup.currenttime
        if current_time:
            return pytz.utc.localize(
                datetime.strptime(current_time.text, DATETIME_FORMAT)
            )

    @property
    def cached_until(self):
        cached_until = self._soup.cacheduntil
        if cached_until:
            return pytz.utc.localize(
                datetime.strptime(cached_until.text, DATETIME_FORMAT)
            )

    @property
    def cached_until_utc(self):
        cached_until = self._soup.cacheduntil
        if cached_until:
            return datetime.strptime(cached_until.text, DATETIME_FORMAT)

    @property
    def is_refreshable(self):
        """
        Returns True/False if this response can be reloaded from EVE API
        servers.
        """
        if self.cached_until:
            return datetime.utcnow() > self.cached_until_utc

        return True
