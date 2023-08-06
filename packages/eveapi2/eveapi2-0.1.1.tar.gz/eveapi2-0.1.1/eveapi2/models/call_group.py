from ..mixins import IterMixin, TagMixin
from ..utils import handle_int


class CallGroup(IterMixin, TagMixin):

    @property
    def group_id(self):
        return handle_int(self._tag.get('groupid'))

    @property
    def name(self):
        return self._tag.get('name')

    @property
    def description(self):
        return self._tag.get('description')
