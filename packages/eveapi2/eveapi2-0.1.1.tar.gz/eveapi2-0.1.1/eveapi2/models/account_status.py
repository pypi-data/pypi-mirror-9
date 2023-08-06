from ..mixins import IterMixin, TagMixin
from ..utils import handle_datetime, handle_int


class AccountStatus(IterMixin, TagMixin):

    @property
    def paid_until(self):
        return handle_datetime(self._tag.paiduntil.text)

    @property
    def create_date(self):
        return handle_datetime(self._tag.createdate.text)

    @property
    def logon_count(self):
        return handle_int(self._tag.logoncount.text)

    @property
    def logon_minutes(self):
        return handle_int(self._tag.logonminutes.text)

    @property
    def multi_character_training(self):
        pass
