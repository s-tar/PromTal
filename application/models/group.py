from application.db import db


class Group(db.Model):
    __tablename__ = "groups"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    def __repr__(self):
        return "<Group {name}>".format(name=self.name)

