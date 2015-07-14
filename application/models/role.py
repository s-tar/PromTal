from application.db import db


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
    photo = db.Column(db.String)

    def __repr__(self):
        return "<Role is {role}>".format(role=self.name)
