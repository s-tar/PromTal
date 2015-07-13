from application import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(64))
    mobile_phone = db.Column(db.String(15))
    inner_phone = db.Column(db.String(4))
    email = db.Column(db.String)
    birth_date = db.Column(db.Date)
    avatar = db.Column(db.String)

    def __repr__(self):
        return "<User {login}>".format(login=self.login)
