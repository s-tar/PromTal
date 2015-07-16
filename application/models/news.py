from application.db import db
from datetime import datetime


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


class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True) 
    title = db.Column(db.String(255))
    text = db.Column(db.Text())
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('news_category.id'))
    datetime = db.Column(db.DateTime, default=datetime.now)

    author = db.relationship("User", backref="news")
    category = db.relationship("NewsCategory", backref="news")
    tags = db.relationship("NewsTag", secondary="NewsTagAssociation", backref="news")
    comments = db.relationship("Comment", secondary="NewsCommentAssociation", backref="news")


