from ..mixins import IterMixin, TagMixin
from ..utils import handle_int


class Character(IterMixin, TagMixin):

    @property
    def character_id(self):
        return handle_int(self._tag.get('characterid'))

    @property
    def name(self):
        return self._tag.get('name') or self._tag.get('charactername')

    @property
    def corporation_id(self):
        value2 = self._tag.corporationid
        if value2:
            value2 = value2.text

        return handle_int(self._tag.get('corporationid') or value2)

    @property
    def corporation_name(self):
        return self._tag.get('corporationname') or self._tag.corporation.text

    @property
    def alliance_id(self):
        return handle_int(
            self._tag.get('allianceid') or self._tag.allianceid.text
        )

    @property
    def alliance_name(self):
        value2 = self._tag.alliance
        if value2:
            value2 = value2.text

        return self._tag.get('alliancename') or value2

    @property
    def faction_id(self):
        return handle_int(self._tag.get('factionid'))

    @property
    def faction_name(self):
        return self._tag.get('factionname')

    @property
    def race(self):
        return self._tag.race.text

    @property
    def bloodline(self):
        return self._tag.bloodline.text

    @property
    def corporation_date(self):
        pass
