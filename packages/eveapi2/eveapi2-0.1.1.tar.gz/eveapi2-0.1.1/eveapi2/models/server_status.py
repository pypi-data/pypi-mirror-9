from ..mixins import IterMixin, TagMixin
from ..utils import handle_boolean


class ServerStatus(IterMixin, TagMixin):

    @property
    def server_open(self):
        return handle_boolean(self._tag.serveropen.text)

    @property
    def online_players(self):
        return int(self._tag.onlineplayers.text)
