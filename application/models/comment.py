from application.db import db
from datetime import datetime


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    text = db.Column(db.Text())
    datetime = db.Column(db.DateTime, default=datetime.now)

    quote_for_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    quote_for = db.relationship('Comment', remote_side=[id],  backref="quotes")

    def to_json(self):
        return {
            'id': self.id,
            'author_id': self.author_id,
            'text': self.text,
            'datetime': self.datetime,
            'quote_for_id': self.quote_for_id,
            'quote_for': self.quote_for,
        }