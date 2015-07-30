from application.db import db


class Department(db.Model):
    __tablename__ = 'department'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    parent_id = db. Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    parent = db.relationship('Department', remote_side=[id],  backref="subdepartment")
    user = db.relationship("User", backref="managed_department", foreign_keys=[user_id])

    def __repr__(self):
        return "<Department {name}>".format(name=self.name)

    @classmethod
    def get_all(cls):
        return cls.query.all()
