from __future__ import absolute_import, unicode_literals

import ujson as json

from django.utils.encoding import force_bytes, force_text


from django_redis.serializers.base import BaseSerializer


class UJSONSerializer(BaseSerializer):
    def dumps(self, value):
        return force_bytes(json.dumps(value))

    def loads(self, value):
        return json.loads(force_text(value))
