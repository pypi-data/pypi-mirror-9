from bs4.element import Tag

from ..mixins import IterMixin, TagMixin
from ..utils import handle_datetime, handle_int


class Alliance(IterMixin, TagMixin):

    def __str__(self):
        return str(self.short_name)

    @property
    def name(self):
        return self._tag.get('name')

    @property
    def short_name(self):
        return self._tag.get('shortname')

    @property
    def alliance_id(self):
        return handle_int(self._tag.get('allianceid'))

    @property
    def executor_corp_id(self):
        return handle_int(self._tag.get('executorcorpid'))

    @property
    def member_count(self):
        return handle_int(self._tag.get('membercount'))

    @property
    def start_date(self):
        return handle_datetime(self._tag.get('startdate'))

    @property
    def member_corporations(self):
        for row in self._tag.rowset.children:
            if isinstance(row, Tag):
                yield MemberCorporation(row)


class MemberCorporation(IterMixin, TagMixin):

    def __str__(self):
        return self.corporation_id

    @property
    def corporation_id(self):
        return handle_int(self._tag.get('corporationid'))

    @property
    def start_date(self):
        return handle_datetime(self._tag.get('startdate'))
