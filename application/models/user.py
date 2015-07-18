from application.db import db
from datetime import datetime, timedelta
from uuid import uuid1


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)  # TODO check, if autoincrement
    login = db.Column(db.String(64), unique=True)
    full_name = db.Column(db.String(64))
    mobile_phone = db.Column(db.String, nullable=True)  # TODO Add constraint on length and format
    inner_phone = db.Column(db.String, nullable=True)   # TODO Add constraint on length and format
    email = db.Column(db.String)  # TODO Add constraint on length; can't be nullable in future
    birth_date = db.Column(db.Date, nullable=True)  # TODO Add default value
    avatar = db.Column(db.String, nullable=True)
    skype = db.Column(db.String(64), unique=True)

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
        restore = cls.query.filter_by(token=token, is_active=True)
        restore = restore.filter(PasswordRestore.datetime>=expiration)
        restore = restore.first()
        return restore

    @classmethod
    def deactivation_token(cls, token_obj):
        tokens = cls.query.filter_by(author_id=token_obj.author_id).all()
        for token in tokens:
            token.is_active=False
            db.session.add(token)
        db.session.commit()

