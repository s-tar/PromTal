__author__ = 'newbie'

from marshmallow import Schema, fields

from application.models.serializers.user import UserSchema


class CommentSchema(Schema):

    id = fields.Int()
    text = fields.Str()
    datetime = fields.DateTime()
    entity = fields.Str()
    entity_id = fields.Int()

    quote_for = fields.Nested('self', exclude=('quote_for', ))
    author = fields.Nested(UserSchema, many=True)

comment_schema = CommentSchema()