from datetime import datetime
from application.db import db
from application.models.comment import Comment, HasComments
from application.models.mixin import Mixin
from application.models.news_category import NewsCategory
from application.models.news_tag import NewsTag
from application.models.serializers.news import news_schema
from application.models.vote import HasVotes
from sqlalchemy import event


class NewsTagAssociation(db.Model):
    __tablename__ = 'news_tag_association'

    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('news_tag.id'))


class News(db.Model, Mixin, HasComments, HasVotes):
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
    votes_count = db.Column(db.Integer, default=0)
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

    def after_delete_comment(self, comment=None):
        self.__recount_comments()

    def after_add_comment(self, comment=None):
        self.__recount_comments()

    def __recount_comments(self):
        self.comments_count = len([c for c in self.comments_all if c.status != Comment.Status.DELETED])

    def after_delete_vote(self, vote=None):
        self.votes_count = (self.votes_count or 0) - 1

    def after_add_vote(self, vote=None):
        self.votes_count = (self.votes_count or 0) + 1

    def after_update_vote(self, value):
        self.votes_count = (self.votes_count or 0) + value

    def to_json(self):
        return news_schema.dump(self)

News.init_comments()
News.init_votes()
