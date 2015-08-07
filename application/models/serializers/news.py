__author__ = 'newbie'

from marshmallow import Schema, fields

from application.models.serializers.user import UserSchema
from application.models.serializers.custom_fields import StatusField


class NewsCategorySchema(Schema):

    id = fields.Int()
    name = fields.Str()

    parent = fields.Nested('self', exclude=('parent', ))


class NewsTagSchema(Schema):

    id = fields.Int()
    name = fields.Str()


class NewsSchema(Schema):

    id = fields.Int()
    title = fields.Str()
    text = fields.Str()
    status = StatusField()
    datetime = fields.DateTime()
    comments_count = fields.Int()
    likes_count = fields.Int()
    views_count = fields.Int()

    author = fields.Nested(UserSchema)
    category = fields.Nested(NewsCategorySchema, many=True)
    tags = fields.Nested(NewsTagSchema, many=True)

news_schema = NewsSchema()
news_category = NewsCategorySchema()
news_tag = NewsTagSchema()
