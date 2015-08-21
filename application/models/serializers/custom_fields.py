from datetime import datetime

from marshmallow import fields


class StatusField(fields.Field):

    def _serialize(self, value, attr, obj):
        if value is None:
            return {}
        return {'value': obj.status, 'title': dict(obj.STATUSES).get(obj.status)}


class RolesField(fields.Field):

    def _serialize(self, value, attr, obj):
        if value is None:
            return []
        return [{'id': x.id, 'name': x.name} for x in obj.roles]


class DateTimeField(fields.DateTime):

    def _deserialize(self, value):
        if value == '':
            return
        return fields.DateTime._deserialize(self, value)
