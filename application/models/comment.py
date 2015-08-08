from enum import Enum
from application.models.file import File
from datetime import datetime as _datetime
from collections import defaultdict

from application.db import db
from application.models.mixin import Mixin
from application.models.serializers.comment import comment_schema
from application.models.vote import HasVotes, Vote
from application.utils import auth
from sqlalchemy import event, select, and_, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, Session, object_session
import application
from sqlalchemy import orm


class Comment(db.Model, Mixin, HasVotes):

    class Status:
        (
            ACTIVE,
            DELETED,
            MODIFIED
        ) = range(3)

        TITLES = dict([(ACTIVE, 'active'), (DELETED, 'deleted'), (MODIFIED, 'modified')])

    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    text = db.Column(db.Text())
    datetime = db.Column(db.DateTime, default=_datetime.now)
    modify_datetime = db.Column(db.DateTime, default=_datetime.now)
    entity = db.Column(db.String(255))
    entity_id = db.Column(db.Integer)
    quote_for_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    status = db.Column(db.Integer, default=Status.ACTIVE)
    votes_count = db.Column(db.Integer, default=0)
    quote_for = db.relationship('Comment', remote_side=[id], order_by="Comment.datetime", backref=backref("quotes", cascade="all"))
    author = db.relationship("User", backref="comments", lazy='joined')

    @orm.reconstructor
    def init_on_load(self):
        self.__my_vote = None
        self.__files = []

    @hybrid_property
    def my_vote(self):
        return self.__my_vote

    @my_vote.setter
    def my_vote_setter(self, val):
        self.__my_vote = val

    def add_file(self, file):
        self.__files.append(file)

    @hybrid_property
    def files(self):
        if self.__files:
            return self.__files
        return File.get(module='comments', entity=self)

    @files.setter
    def files_setter(self, files):
        self.__files = files

    def to_json(self):
        return comment_schema.dump(self)

    @staticmethod
    def get_for(entity, entity_id, lazy=True):
        user = auth.service.get_user()
        if lazy:
            return Comment.query.filter(Comment.entity == entity, Comment.entity_id == entity_id, Comment.quote_for_id == None) \
                .order_by(Comment.datetime.desc()).all()
        else:
            query = Comment.query.filter(Comment.entity == entity, Comment.entity_id == entity_id) \
                .outerjoin(Vote, and_(Vote.entity == Comment.__tablename__, Vote.entity_id == Comment.id, Vote.user == user)) \
                .outerjoin(File, File.entity == func.concat(Comment.__tablename__, '.', Comment.id)) \
                .add_entity(Vote) \
                .add_entity(File) \
                .order_by(Comment.datetime.desc(), File.id)
            comments_votes_files = query.all()
            comments = []
            for comment, vote, file in comments_votes_files:
                if file:
                    comment.add_file(file)
                comment.my_vote = vote
                comments.append(comment)
            return comments

    def get_entity(self):
        return Comment.get_entities().get(self.entity, {}).get(self.entity_id)

    @staticmethod
    def get_entities():
        return HasComments.__entities__

    def after_delete_vote(self, vote=None):
        self.votes_count = (self.votes_count or 0) - 1

    def after_add_vote(self, vote=None):
        self.votes_count = (self.votes_count or 0) + 1

    def after_update_vote(self, value):
        self.votes_count = (self.votes_count or 0) + value


@event.listens_for(Comment, "after_delete")
def after_comment_delete(mapper, connection, target):
    for f in target.files:
        f.remove_files()
        session = Session.object_session(f)
        session.delete(f)

Comment.init_votes()


class HasComments:
    __comments = None
    __entities__ = {}

    @property
    def entity(self):
        return self.get_entity()

    def get_entity(self):
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
        HasComments.__entities__[cls.__tablename__] = cls
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

