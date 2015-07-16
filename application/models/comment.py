from application.db import db
from datetime import datetime


class Comments(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.Text())
    datetime = db.Column(db.DateTime, default=datetime.now)

    quote_for_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    quote_for = db.relationship('Comments', remote_side=[id],  backref="quotes")

