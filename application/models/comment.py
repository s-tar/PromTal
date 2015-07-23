from application.db import db
from datetime import datetime


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    entity = db.Column(db.String(255))
    entity_id = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    text = db.Column(db.Text())
    datetime = db.Column(db.DateTime, default=datetime.now)
    quote_for_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)

    quote_for = db.relationship('Comment', remote_side=[id], order_by="Comment.datetime", backref="quotes")
    author = db.relationship("User", backref="comments")

    @staticmethod
    def get_for(entity, entity_id):
        return Comment.query.filter(Comment.entity == entity, Comment.entity_id == entity_id)\
            .order_by(Comment.datetime.desc()).all()