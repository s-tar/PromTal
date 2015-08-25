from application.db import db


class ViewUsers4Search(db.Model):
    __tablename__ = 'view_users4search'
    users_id = db.Column(db.Integer, primary_key=True)
    users_full_name = db.Column(db.String(64))
    users_login = db.Column(db.String(64))
    users_email = db.Column(db.String)
    users_status = db.Column(db.Integer)
    users_mobile_phone = db.Column(db.String, nullable=True)
    users_inner_phone = db.Column(db.String, nullable=True)
    users_birth_date = db.Column(db.DateTime, nullable=True)
    users_skype = db.Column(db.String(64), nullable=True)
    users_position = db.Column(db.String(255))
    department_name = db.Column(db.String(255))
    photo_url = db.Column(db.String(255))

    def __repr__(self):
        return "<ViewUsers4Search {name}>".format(name=self.users_login)