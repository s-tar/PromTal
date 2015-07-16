from application.db import db


class NewsTag(db.Model):
    __tablename__ = 'news_tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
