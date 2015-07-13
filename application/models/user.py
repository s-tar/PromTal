from application import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), unique=True)
    full_name = db.Column(db.String(64))
    mobile_phone = db.Column(db.String(15), nullable=True)
    inner_phone = db.Column(db.String(4), nullable=True)
    email = db.Column(db.String, unique=True)
    birth_date = db.Column(db.Date, nullable=True)
    avatar = db.Column(db.String, nullable=True)

    def __repr__(self):
        return "<User {login}>".format(login=self.login)
