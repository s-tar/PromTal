from application.db import db


class Team(db.Model):
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    parent_id = db. Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    parent = db.relationship('Team', remote_side=[id],  backref="subcategories")
    user = db.relationship("User", backref="team")
