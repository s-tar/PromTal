from datetime import datetime, timedelta, date
from uuid import uuid1
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import ARRAY

from application.db import db
from application.lib.orm import MutableList, EnumInt
from application.models.mixin import Mixin
from application.utils.auth.user import User as AuthUser


class User(db.Model, AuthUser):
    __tablename__ = 'users'

    # STATUS = EnumInt('Statuses', {
    #     'active': 0,
    #     'deleted': 1,
    #     'blocked': 2,
    # })
    #
    # ROLE = EnumInt('Roles', {
    #     'user': 0,
    #     'admin': 1,
    #     'moderator': 2,
    # })

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)  # TODO Add constraint on length; can't be nullable in future
    full_name = db.Column(db.String(64))
    login = db.Column(db.String(64), unique=True)
    # status = db.Column(EnumInt(STATUS), default=STATUS.active)
    # roles = db.Column(MutableList.as_mutable(ARRAY(EnumInt(ROLE))), default=[ROLE.user])
    mobile_phone = db.Column(db.String, nullable=True)  # TODO Add constraint on length and format
    inner_phone = db.Column(db.String, nullable=True)   # TODO Add constraint on length and format
    birth_date = db.Column(db.Date, nullable=True)  # TODO Add default value
    avatar = db.Column(db.String, nullable=True)  # TODO delete this field
    photo = db.Column(db.String(255), nullable=True)
    photo_s = db.Column(db.String(255), nullable=True)
    skype = db.Column(db.String(64), unique=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))

    department = db.relationship("Department", backref="users")
    team = db.relationship("Team", backref="users")


    def __repr__(self):
        return "<User {login}>".format(login=self.login)

    @classmethod
    def get_by_id(cls, uid):
        return cls.query.filter_by(id=uid).first()

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def get_by_login(cls, login):
        return cls.query.filter_by(login=login).first()

    @classmethod
    def edit_user(cls, uid, full_name=full_name,
                            mobile_phone=mobile_phone,
                            inner_phone=inner_phone,
                            email=email,
                            birth_date=birth_date,
                            skype=skype,
                            photo=photo,
                            photo_s=photo_s):
        u = cls.query.filter_by(id=uid).first()
        if u:
            u.full_name = full_name
            u.mobile_phone = mobile_phone
            u.inner_phone = inner_phone
            u.email = email
            u.birth_date = birth_date
            u.skype = skype
            if photo:
                u.photo = photo
            if photo_s:
                u.photo_s = photo_s
            db.session.add(u)
            db.session.commit()
        return u

    @property
    def age(self):
        today, born = date.today(), self.birth_date
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    def to_json(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'login': self.login,
            # 'status': type(self.status),
            # 'roles': type(self.roles),
            'mobile_phone': self.mobile_phone,
            'inner_phone': self.inner_phone,
            'birth_date': self.birth_date,
            'avatar': self.avatar,
            'photo': self.photo,
            'skype': self.skype,
        }


class PasswordRestore(db.Model):
    __tablename__ = 'password_restore'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    token = db.Column(db.String(64))
    is_active = db.Column(db.Boolean, default=True)
    datetime = db.Column(db.DateTime, default=datetime.now)

    author = db.relationship("User", backref="password_restore")

    def __repr__(self):
        return "<PasswordRestore {token}>".format(token=self.token)

    @classmethod
    def add_token(cls, user):
        token = ''.join(str(uuid1()).split('-'))
        pass_restore = PasswordRestore(author_id=user.id, token=token)
        db.session.add(pass_restore)
        db.session.commit()
        return token

    @classmethod
    def is_valid_token(cls, token):
        expiration = datetime.now() - timedelta(days=1)
        restore_pass = cls.query.filter(PasswordRestore.token == token,
                                   PasswordRestore.is_active == True,
                                   PasswordRestore.datetime >= expiration).first()
        return restore_pass

    @classmethod
    def deactivation_token(cls, token_obj):
        tokens = cls.query.filter(PasswordRestore.author_id == token_obj.author_id).all()
        for token in tokens:
            token.is_active = False
        db.session.commit()
