from application.db import db
from datetime import datetime

news_tag_association_table = db.Table('news_tag_association', db.Model,
    db.Column('news_id', db.Integer, db.ForeignKey('news.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('news_tag.id')))

news_comment_association_table = db.Table('news_comment_association', db.Model,
    db.Column('news_id', db.Integer, db.ForeignKey('news.id')),
    db.Column('comment_id', db.Integer, db.ForeignKey('comment.id')))


class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True) 
    title = db.Column(db.String(255))
    text = db.Column(db.Text())
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('news_category.id'))
    datetime = db.Column(db.DateTime, default=datetime.now)

    author = db.relationship("User", backref="news")
    category = db.relationship("NewsCategory", backref="news")
    tags = db.relationship("NewsTag", secondary=news_tag_association_table, backref="news")
    comments = db.relationship("Comment", secondary=news_comment_association_table, backref="news")


