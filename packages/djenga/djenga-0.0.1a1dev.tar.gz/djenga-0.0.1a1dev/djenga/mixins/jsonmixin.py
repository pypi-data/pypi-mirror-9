# encoding: utf-8
# pylint: disable=pointless-string-statement


class JsonMixin(object):
    def to_json(self):
        mp = {}
        rg_fields = self._meta.get_all_field_names()
        for x in rg_fields:
            mp[x] = getattr(self, x, None)
        return mp