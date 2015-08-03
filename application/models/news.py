from datetime import datetime, date, timedelta

from application.db import db
from application.models.comment import Comment, HasComments
from application.models.mixin import Mixin
from application.models.news_category import NewsCategory
from application.models.news_tag import NewsTag
from application.models.serializers.news import news_schema


class NewsTagAssociation(db.Model):
    __tablename__ = 'news_tag_association'

    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('news_tag.id'))


class News(db.Model, Mixin, HasComments):
    __tablename__ = 'news'

    (
        STATUS_ACTIVE,
        STATUS_DELETED,
        STATUS_BLOCKED,
    ) = range(3)

    STATUSES = [(STATUS_ACTIVE, 'Active'), (STATUS_DELETED, 'Deleted'), (STATUS_BLOCKED, 'Blocked')]

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    text = db.Column(db.Text())
    status = db.Column(db.Integer, default=STATUS_ACTIVE)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('news_category.id'))
    datetime = db.Column(db.DateTime, default=datetime.now)
    comments_count = db.Column(db.Integer, default=0)
    likes_count = db.Column(db.Integer, default=0)
    views_count = db.Column(db.Integer, default=0)

    author = db.relationship("User", backref="news")
    category = db.relationship("NewsCategory", backref="news")
    tags = db.relationship("NewsTag", secondary="news_tag_association", backref="news")

    @property
    def announcement(self):
        parts = self.text.split('<!-- page break -->')
        return parts[0]

    def increment_views(self):
        self.views_count = (self.views_count or 0) + 1
        db.session.commit()

    def after_add_comment(self, comment=None):
        self.comments_count = (self.comments_count or 0) + 1
        db.session.commit()

    def to_json(self):
        return news_schema.dump(self)

News.init_comments()
