from datetime import datetime
from application import db
from application.models.mixin import Mixin
from application.models.user import User
__author__ = 's.taran'


class Community(db.Model, Mixin):
    __tablename__ = 'community'

    class STATUS:
        (
            ACTIVE,
            DELETED,
        ) = range(2)
        TITLE = dict([(ACTIVE, 'active'), (DELETED, 'deleted')])

    class TYPE:
        (
            PUBLIC,
            PRIVATE,
        ) = range(2)
        TITLE = dict([(PUBLIC, 'public'), (PRIVATE, 'private')])

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    image_id = db.Column(db.Integer, db.ForeignKey('file.id'))
    create_date = db.Column(db.DateTime, default=datetime.now)
    type = db.Column(db.Integer, default=TYPE.PUBLIC)
    status = db.Column(db.Integer, default=STATUS.ACTIVE)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    owner = db.relationship("User", backref="community", lazy="joined")
    image = db.relationship("File", backref="community", lazy="joined")

    members = db.relationship("User", secondary="community_member", backref="communities")

    def is_member(self, user):
        return user is self.owner or user in self.members


class CommunityMember(db.Model):
    __tablename__ = 'community_member'

    class STATUS:
        (
            ACCEPTED,
            WAITING,
            REJECTED,
        ) = range(3)
        TITLE = dict([(ACCEPTED, 'accepted'), (WAITING, 'waiting'), (REJECTED, 'rejected')])

    community_id = db.Column(db.Integer, db.ForeignKey(Community.id), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key=True)
    status = db.Column(db.Integer, default=STATUS.WAITING)