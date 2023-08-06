from ..mixins import IterMixin, TagMixin
from ..utils import handle_int


class Call(IterMixin, TagMixin):

    @property
    def access_mask(self):
        return self._tag.get('accessmask')

    @property
    def type(self):
        return self._tag.get('type')

    @property
    def name(self):
        return self._tag.get('name')

    @property
    def group_id(self):
        return handle_int(self._tag.get('groupid'))

    @property
    def description(self):
        return self._tag.get('description')
