from enum import Enum
from application.models.file import File
from datetime import datetime as _datetime
from application.utils import auth
from collections import defaultdict

from application.db import db
from application.models.mixin import Mixin
from application.models.serializers.comment import comment_schema
from sqlalchemy import event
from sqlalchemy.orm import backref, Session, class_mapper


class Vote(db.Model, Mixin):

    class Type:
        (
            LIKE,
            VOTE
        ) = range(2)

        TITLES = dict([(LIKE, 'like'), (VOTE, 'vote')])

    class Value:
        POSITIVE = 1
        NEGATIVE = -1
        NEUTRAL = 0

        TITLES = dict([(POSITIVE, 'positive'), (NEGATIVE, 'negative'), (NEUTRAL, 'neutral')])

    __tablename__ = 'vote'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    datetime = db.Column(db.DateTime, default=_datetime.now)
    value = db.Column(db.Integer, default=Value.NEUTRAL)
    entity = db.Column(db.String(255))
    entity_id = db.Column(db.Integer)
    type = db.Column(db.Integer, default=Type.VOTE)
    user = db.relationship("User", backref="votes",)

    @staticmethod
    def get_for(entity, entity_id, user=None):
        query = Vote.query.filter(Vote.entity == entity, Vote.entity_id == entity_id)
        if user: query = query.filter(Vote.user == user)
        return query.first() if user else query.all()

    def get_entity(self):
        return Vote.get_entities().get(self.entity, {}).get(self.entity_id)

    @staticmethod
    def get_entities():
        return HasVotes.__entities__


class HasVotes:
    __entities__ = {}

    @property
    def entity(self):
        return {'name': self.__tablename__, 'id': self.id}

    @property
    def votes(self):
        return Vote.get_for(self.entity['name'], self.entity['id'])

    @property
    def my_vote(self):
        user = auth.service.get_user()
        return Vote.get_for(self.entity['name'], self.entity['id'], user)

    @classmethod
    def init_votes(cls):
        cls.__entities__[cls.__tablename__] = cls
        event.listen(cls, 'after_delete', HasVotes.after_entity_delete)

    @staticmethod
    def after_entity_delete(mapper, connection, target):
        for v in target.votes:
            session = Session.object_session(v)
            session.delete(v)

    def after_add_vote(self, vote=None):
        pass

    def after_delete_vote(self, vote=None):
        pass

