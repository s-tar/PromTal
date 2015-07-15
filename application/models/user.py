from application.db import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)  # TODO check, if autoincrement
    login = db.Column(db.String(64), unique=True)
    full_name = db.Column(db.String(64), index=True)
    mobile_phone = db.Column(db.String, nullable=True)  # TODO Add constraint on length and format
    inner_phone = db.Column(db.String, nullable=True)   # TODO Add constraint on length and format
    email = db.Column(db.String, unique=True)  # TODO Add constraint on length; can't be nullable in future
    birth_date = db.Column(db.Date, nullable=True)  # TODO Add default value
    avatar = db.Column(db.String, nullable=True)

    def __repr__(self):
        return "<User {login}>".format(login=self.login)
