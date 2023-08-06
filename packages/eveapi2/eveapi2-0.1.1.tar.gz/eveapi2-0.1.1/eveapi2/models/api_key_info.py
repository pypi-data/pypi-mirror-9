from bs4.element import Tag

from .character import Character
from ..mixins import IterMixin, TagMixin
from ..utils import handle_datetime


class APIKeyInfo(IterMixin, TagMixin):

    @property
    def access_mask(self):
        return self._tag.get('accessmask')

    @property
    def type(self):
        return self._tag.get('type')

    @property
    def expires(self):
        return handle_datetime(self._tag.get('expires'))

    @property
    def characters(self):
        for row in self._tag.rowset.children:
            if isinstance(row, Tag):
                yield Character(row)
