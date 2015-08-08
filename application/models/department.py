from application.db import db
from application.models.user import User


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
    def get_by_id(cls, uid):
        return cls.query.filter_by(id=uid).first()

    @classmethod
    def get_parent_all(cls, uid):
        return cls.query.filter(Department.id!=uid).all()

    @classmethod
    def get_all(cls):
        return cls.query.order_by(Department.name).all()

    @classmethod
    def set_parent(cls, uid, pid):
        dep = cls.query.filter_by(id=uid).first()
        dep.parent_id = pid
        db.session.add(dep)
        db.session.commit()

    @classmethod
    def rename(cls, uid, new_name):
        dep = cls.query.filter_by(id=uid).first()
        dep.name = new_name
        db.session.add(dep)
        db.session.commit()

    @classmethod
    def add(cls, uid, new_name):
        dep = Department(parent_id=uid, name=new_name)
        db.session.add(dep)
        db.session.commit()

    @classmethod
    def delete(cls, uid):
        parent_dep = cls.query.filter_by(parent_id=uid)
        if (parent_dep.count() == 0) and (User.count_users_in_department(uid) == 0):
            cls.query.filter_by(id=uid).delete()
            db.session.commit()
