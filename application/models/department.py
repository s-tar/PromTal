from application.db import db
from application.models.mixin import Mixin
from application.models.user import User


class Department(db.Model, Mixin):
    __tablename__ = 'department'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    parent_id = db. Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    parent = db.relationship('Department', remote_side=[id],  backref="subdepartment")
    user = db.relationship("User", backref="managed_department", foreign_keys=[user_id], lazy='joined')

    @property
    def workers(self):
        return [user for user in self.users if user != self.user]

    def __repr__(self):
        return "<Department {name}>".format(name=self.name)

    @classmethod
    def get_by_id(cls, uid):
        return cls.query.filter_by(id=uid).first()

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def get_parent_all(cls, uid):
        return cls.query.filter(Department.id!=uid).order_by(Department.name).all()

    @classmethod
    def get_all(cls):
        return cls.query.order_by(Department.name).all()

    @classmethod
    def set_parent(cls, uid, pid):
        dep = cls.query.filter_by(id=uid).first()
        if pid == '0':
            dep.parent_id = None
        else:
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
    def add_head4dep(cls, option, dep_id, user_id):
        deps = cls.query.filter_by(user_id=user_id).all()
        for dep in deps:
            dep.user_id = None
            db.session.add(dep)
        dep = cls.query.filter_by(id=dep_id).first()
        if option == 1:
            dep.user_id = user_id
        elif option == 2:
            dep.user_id = None
        db.session.add(dep)
        db.session.commit()

    @classmethod
    def is_user_head(cls, dep_id, user_id):
        dep = cls.query.filter_by(id=dep_id).first()
        if dep.user_id == user_id:
            return True
        return False

    @classmethod
    def get_dep_if_user_head(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()

    @classmethod
    def count_users_in_dep_tree(cls, dep_id):
        dep = cls.query.filter_by(id=dep_id).first()
        c_u = User.count_users_in_department(dep_id)
        def count_users_recursively(dep):
            dep_childs = cls.query.filter_by(parent_id=dep.id).all()
            count_users = 0
            for dep_child in dep_childs:
                count_users += User.count_users_in_department(dep_child.id)
                count_users += count_users_recursively(dep_child)
            return count_users
        c_u += count_users_recursively(dep)
        return c_u - 1

    @classmethod
    def get_head_user_in_dep_tree(cls, dep_id, user_id):
        dep = cls.query.filter_by(id=dep_id).first()
        def head_user_recursively(dep):
            if dep.user_id:
                return User.get_by_id(dep.user_id)
            if dep.parent_id:
                dep_parent = cls.query.filter_by(id=dep.parent_id).first()
                return head_user_recursively(dep_parent)
            return None
        if dep.user_id == user_id:
            if dep.parent_id:
                dep_parent = cls.query.filter_by(id=dep.parent_id).first()
                return head_user_recursively(dep_parent)
            return None
        return head_user_recursively(dep)
    

    @classmethod
    def delete(cls, uid):
        parent_dep = cls.query.filter_by(parent_id=uid)
        if (parent_dep.count() == 0) and (User.count_users_in_department(uid) == 0):
            cls.query.filter_by(id=uid).delete()
            db.session.commit()
