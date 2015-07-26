from application.models.mixin import Mixin
from collections import defaultdict
from application.db import db
from datetime import datetime

class Comment(db.Model, Mixin):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    text = db.Column(db.Text())
    datetime = db.Column(db.DateTime, default=datetime.now)
    entity = db.Column(db.String(255))
    entity_id = db.Column(db.Integer)
    quote_for_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)

    quote_for = db.relationship('Comment', remote_side=[id], order_by="Comment.datetime", backref="quotes")
    author = db.relationship("User", backref="comments", lazy='joined')


    @staticmethod
    def get_for(entity, entity_id, lazy=True):
        if lazy:
            return Comment.query.filter(Comment.entity == entity, Comment.entity_id == entity_id, Comment.quote_for_id is None)\
                .order_by(Comment.datetime.desc()).all()
        else:
            return Comment.query.filter(Comment.entity == entity, Comment.entity_id == entity_id)\
                .order_by(Comment.datetime.desc()).all()

    def get_entity(self):
        return Comment.get_entities().get(self.entity, {}).get(self.entity_id)

    @staticmethod
    def get_entities():
        return HasComments.__entities__


class HasComments:
    __comments = None
    __entities__ = {}

    @property
    def entity(self):
        return {'name': self.__tablename__, 'id': self.id}

    @property
    def comments_all(self):
        return Comment.get_for(self.entity['name'], self.entity['id'], lazy=False)

    @property
    def comments(self):
        if self.__comments is None:
            comments = Comment.get_for(self.entity['name'], self.entity['id'])
            d = defaultdict(list)
            for c in comments:
                d[c.quote_for_id].append(c)
            self.__comments = comments
        return self.__comments

    @classmethod
    def init_comments(cls):
        cls.__entities__[cls.__tablename__] = cls

    def after_add_comment(self, comment=None):
        pass

    def after_delete_comment(self, comment=None):
        pass