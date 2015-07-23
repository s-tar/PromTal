from application.db import db
from datetime import datetime, date, timedelta
from application.models.comment import Comment
from application.models.mixin import Mixin


class NewsTagAssociation(db.Model):
    __tablename__ = 'news_tag_association'
    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('news_tag.id'))


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

    __comments = None

    @property
    def comments(self):
        if self.__comments is None:
            self.__comments = Comment.get_for(self.__tablename__, self.id)
        print('---------->', self.__comments)
        return self.__comments

    @property
    def announcement(self):
        parts = self.text.split('<!-- page break -->')
        return parts[0]



