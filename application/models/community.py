from datetime import datetime
from application import db
from application.models.mixin import Mixin
from application.models.post import Post
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
    community_members = db.relationship("CommunityMember", backref=db.backref("community"), lazy='joined')
    posts = db.relationship("Post", backref="community", order_by=(Post.datetime.desc()))

    def has_member(self, user):
        return user is self.owner or user in self.members

    def member_status_title(self, user):
        status = self.member_status(user)
        return None if status is None else CommunityMember.STATUS.TITLE[status]

    def member_status(self, user):
        try:
            cm = next(cm for cm in self.community_members if cm.user == user)
            return cm.status
        except StopIteration:
            return None

    @property
    def count_members(self):
        return len([cm for cm in self.community_members if cm.status == cm.STATUS.ACCEPTED]) + 1

    @classmethod
    def all_active(cls):
        return cls.query.filter(cls.status == cls.STATUS.ACTIVE).order_by(cls.id.desc()).all()


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

    user = db.relationship(User, backref=db.backref("community_members"))