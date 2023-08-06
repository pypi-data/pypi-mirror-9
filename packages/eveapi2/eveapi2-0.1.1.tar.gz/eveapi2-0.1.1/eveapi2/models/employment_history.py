from ..mixins import IterMixin, TagMixin
from ..utils import handle_datetime, handle_int


class EmploymentHistory(IterMixin, TagMixin):

    @property
    def record_id(self):
        return handle_int(self._tag.get('recordid'))

    @property
    def corporation_id(self):
        return handle_int(self._tag.get('corporationid'))

    @property
    def corporation_name(self):
        return self._tag.get('corporationname')

    @property
    def start_date(self):
        return handle_datetime(self._tag.get('startdate'))
