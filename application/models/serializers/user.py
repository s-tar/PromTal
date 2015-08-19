__author__ = 'kdegtyarenko'

from marshmallow import Schema, fields
from application.models.serializers.custom_fields import StatusField, RolesField, DateField


class UserSchema(Schema):

    id = fields.Int()
    email = fields.Email(required=True)
    full_name = fields.Str(required=True)
    login = fields.Str()
    status = StatusField()
    is_admin = fields.Boolean()
    roles = RolesField()
    mobile_phone = fields.Str()
    inner_phone = fields.Str()
    birth_date = DateField()
    photo_id = fields.Int()
    department_id = fields.Int()
    skype = fields.Str()
    reg_date = fields.DateTime()


user_schema = UserSchema()