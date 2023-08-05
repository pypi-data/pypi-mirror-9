# encoding: utf-8
# pylint: disable=pointless-string-statement


from django.db import models


class JsonMixin(object):
    def to_json(self):
        mp = {}
        rg_fields = self._meta.get_all_field_names()
        for x in rg_fields:
            try:
                p_field = self._meta.get_field(x)
                if not isinstance(p_field, models.ForeignKey):
                    mp[x] = getattr(self, x, None)
            except models.FieldDoesNotExist:
                pass
        return mp