from enum import Enum
from application.models.file import File
from datetime import datetime
from collections import defaultdict

from application.db import db
from application.models.mixin import Mixin
from application.models.serializers.comment import comment_schema
from sqlalchemy import event
from sqlalchemy.orm import backref, Session


class Comment(db.Model, Mixin):

    class Status:
        (
            ACTIVE,
            DELETED,
        ) = range(2)
        TITLES = dict([(ACTIVE, 'active'), (DELETED, 'deleted')])

    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    text = db.Column(db.Text())
    datetime = db.Column(db.DateTime, default=datetime.now)
    entity = db.Column(db.String(255))
    entity_id = db.Column(db.Integer)
    quote_for_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    status = db.Column(db.Integer, default=Status.ACTIVE)
    quote_for = db.relationship('Comment', remote_side=[id], order_by="Comment.datetime", backref=backref("quotes", cascade="all"))
    author = db.relationship("User", backref="comments", lazy='joined')

    __files = []

    @property
    def files(self):
        if not self.__files:
            self.__files = File.get(module='comments', entity=self)
        return self.__files

    def to_json(self):
        return comment_schema.dump(self)

    @staticmethod
    def get_for(entity, entity_id, lazy=True):
        if lazy:
            return Comment.query.filter(Comment.entity == entity, Comment.entity_id == entity_id, Comment.quote_for_id == None) \
                .order_by(Comment.datetime.desc()).all()
        else:
            return Comment.query.filter(Comment.entity == entity, Comment.entity_id == entity_id) \
                .order_by(Comment.datetime.desc()).all()
            return comments


    def get_entity(self):
        return Comment.get_entities().get(self.entity, {}).get(self.entity_id)

    @staticmethod
    def get_entities():
        return HasComments.__entities__

@event.listens_for(Comment, "after_delete")
def after_comment_delete(mapper, connection, target):
    for f in target.files:
        f.remove_files()
        session = Session.object_session(f)
        session.delete(f)


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
            self.__comments = Comment.get_for(self.entity['name'], self.entity['id'])
        return self.__comments

    @classmethod
    def init_comments(cls):
        cls.__entities__[cls.__tablename__] = cls
        event.listen(cls, 'after_delete', HasComments.after_entity_delete)

    @staticmethod
    def after_entity_delete(mapper, connection, target):
        for c in target.comments:
            session = Session.object_session(c)
            session.delete(c)

    def after_add_comment(self, comment=None):
        pass

    def after_delete_comment(self, comment=None):
        pass

