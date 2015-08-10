__author__ = 'kdegtyarenko'

from marshmallow import Schema, fields
from application.models.serializers.custom_fields import RolesField, StatusField


class UserSchema(Schema):

    id = fields.Int()
    email = fields.Email()
    full_name = fields.Str()
    login = fields.Str()
    status = StatusField()
    is_admin = fields.Boolean()
    mobile_phone = fields.Str()
    inner_phone = fields.Str()
    birth_date = fields.Date()
    avatar = fields.Str()
    photo = fields.Str()
    photo_s = fields.Str()
    skype = fields.Str()

user_schema = UserSchema()