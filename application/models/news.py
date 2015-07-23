from application.db import db
from datetime import datetime, date, timedelta
from application.models.comment import Comment
from application.models.mixin import Mixin


class NewsTagAssociation(db.Model):
    __tablename__ = 'news_tag_association'
    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('news_tag.id'))


class NewsCommentAssociation(db.Model):
    __tablename__ = 'news_comment_association'
    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))


class News(db.Model, Mixin):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True) 
    title = db.Column(db.String(255))
    text = db.Column(db.Text())
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('news_category.id'))
    datetime = db.Column(db.DateTime, default=datetime.now)
    comments_count = db.Column(db.Integer)
    likes_count = db.Column(db.Integer)

    author = db.relationship("User", backref="news")
    category = db.relationship("NewsCategory", backref="news")
    tags = db.relationship("NewsTag", secondary="news_tag_association", backref="news")
    comments = db.relationship("Comment", secondary="news_comment_association", order_by=Comment.datetime.desc(), backref="news")

    @property
    def announcement(self):
        parts = self.text.split('<!-- page break -->')
        return parts[0]



