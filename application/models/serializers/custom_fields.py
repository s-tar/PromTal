__author__ = 'newbie'

from marshmallow import fields


class RolesField(fields.Field):

    def _serialize(self, value, attr, obj):
        if value is None:
            return {}
        roles = dict(obj.ROLES)
        return [{'value': x, 'title': roles.get(x)} for x in obj.roles]


class StatusField(fields.Field):

    def _serialize(self, value, attr, obj):
        if value is None:
            return {}
        return {'value': obj.status, 'title': dict(obj.STATUSES).get(obj.status)}