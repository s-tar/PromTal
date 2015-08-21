from datetime import datetime, timedelta, date
from sqlalchemy import or_, and_, extract
from uuid import uuid1
from application.models.mixin import Mixin
from application.models.file import File
from application.utils import image

from application.db import db
from application.models.serializers.user import user_schema
from application.utils.auth.user import User as AuthUser


role_permission_associate = db.Table('role_permission', db.Model.metadata,
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id')),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'))
)
user_permission_associate = db.Table('user_permission', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'))
)
user_role_associate = db.Table('user_role', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'))
)


class Permission(db.Model):

    __tablename__ = 'permissions'

    PERMISSIONS = [
        ('post_comment', 'Post comment'), ('edit_comments', 'Edit comments'),
        ('write_articles', 'Write articles'), ('moderate_comments', 'Moderate comments'),
        ('manage_users', 'Manage users'), ('set_permissions', 'Set permissions'),
        ('change_company_structure', 'Change company structure'),
        ('manage_user_groups', 'Manage user groups'),
    ]

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    title = db.Column(db.String(64))

    def __repr__(self):
        return "<Permission {name}>".format(name=self.name)

    @classmethod
    def get_by_id(cls, uid):
        return cls.query.filter_by(id=uid).first()

    @classmethod
    def get_all(cls):
        return cls.query.order_by(cls.title).all()


class Role(db.Model):

    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    permissions = db.relationship("Permission", secondary=role_permission_associate, backref="roles")

    def __repr__(self):
        return "<Role {name}>".format(name=self.name)

    @classmethod
    def get_by_id(cls, uid):
        return cls.query.filter_by(id=uid).first()

    @classmethod
    def get_all(cls):
        return cls.query.order_by(cls.name.desc()).all()


class User(db.Model, AuthUser, Mixin):
    '''
    при добавлении полей не забыть их добавить в
    application/models/serializers/users.py для корректной валидации данных
    '''

    __tablename__ = 'users'

    (
        STATUS_ACTIVE,
        STATUS_DELETED,
    ) = range(2)

    STATUSES = [(STATUS_ACTIVE, 'Active'), (STATUS_DELETED, 'Deleted')]

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)  # TODO Add constraint on length; can't be nullable in future
    full_name = db.Column(db.String(64))
    login = db.Column(db.String(64), unique=True)
    status = db.Column(db.Integer, default=STATUS_ACTIVE)
    mobile_phone = db.Column(db.String, nullable=True)  # TODO Add constraint on length and format
    inner_phone = db.Column(db.String, nullable=True)   # TODO Add constraint on length and format
    birth_date = db.Column(db.DateTime, nullable=True)  # TODO Add default value
    skype = db.Column(db.String(64), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    position = db.Column(db.String(255))
    photo_id = db.Column(db.Integer, db.ForeignKey('file.id'))
    is_admin = db.Column(db.Boolean, default=False)
    reg_date = db.Column(db.DateTime, default=datetime.now)

    permissions = db.relationship("Permission", secondary=user_permission_associate, backref="users", lazy='dynamic')
    roles = db.relationship("Role", secondary=user_role_associate, backref="users", lazy='dynamic')
    department = db.relationship("Department", backref="users", foreign_keys=[department_id])
    photo = db.relationship("File", lazy="joined")

    def __repr__(self):
        return "<User {login}>".format(login=self.login)

    @classmethod
    def get_by_id(cls, uid):
        return cls.query.filter_by(id=uid).first()

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def get_by_login(cls, login):
        return cls.query.filter_by(login=login).first()

    @classmethod
    def count_users_in_department(cls, department):
        return cls.query.filter_by(department_id=department).count()

    @classmethod
    def find_user(cls, dep_id, name):
        return cls.query.filter(or_(User.department_id == None, User.department_id != dep_id)).filter(User.full_name.ilike('%'+name+'%')).limit(5).all()

    @classmethod
    def get_new(cls):
        today = date.today()
        delta = today - timedelta(days=30)
        return cls.query.filter(User.reg_date > delta).order_by(User.reg_date.desc(), User.full_name).all()

    @classmethod
    def get_birthday(cls):
        today = date.today()
        tomorrow = today + timedelta(days=1)
        return cls.query.filter(
            or_(
                and_(extract('month', User.birth_date) == today.month, extract('day', User.birth_date) == today.day),
                and_(extract('month', User.birth_date) == tomorrow.month, extract('day', User.birth_date) == tomorrow.day)
            )).order_by(User.birth_date.desc(), User.full_name).all()

    @classmethod
    def set_user_is_admin(cls, user_id):
        u = cls.query.filter_by(id=user_id).first()
        u.is_admin = True
        u.roles = []
        db.session.add(u)
        db.session.commit()

    @classmethod
    def set_user_role(cls, user_id, role_id):
        u = cls.query.filter_by(id=user_id).first()
        r = Role.get_by_id(role_id)
        u.roles = []
        u.roles.append(r)
        u.is_admin = False
        db.session.add(u)
        db.session.commit()

    @classmethod
    def get_user_role_id(cls, user_id):
        u = cls.query.filter_by(id=user_id).first()
        if u.is_admin:
            return 0
        elif u.roles and len(u.roles.all()):
            return u.roles[0].id
        return ''

    @classmethod
    def set_user_per(cls, user_id, per_string):
        if per_string == "None":
            per_list = []
        else:
            per_list = per_string.split(',')
        u = cls.query.filter_by(id=user_id).first()
        u.permissions = []
        for per_id in per_list:
            p = Permission.get_by_id(per_id)
            u.permissions.append(p)
        db.session.add(u)
        db.session.commit()

    @classmethod
    def get_user_permissions_id(cls, user_id):
        u = cls.query.filter_by(id=user_id).first()
        permissions_list = []
        for per in u.permissions:
            permissions_list.append(per.id)
        return permissions_list

    @classmethod
    def add_user2dep(cls, dep_id, user_id):
        u = cls.query.filter_by(id=user_id).first()
        if dep_id == 0:
            dep_id = None
        u.department_id = dep_id
        db.session.add(u)
        db.session.commit()

    @classmethod
    def edit_user(cls, uid, full_name=full_name,
                            position=position,
                            mobile_phone=mobile_phone,
                            inner_phone=inner_phone,
                            email=email,
                            birth_date=birth_date,
                            skype=skype,
                            photo=photo):
        u = cls.query.filter_by(id=uid).first()

        if u:
            u.full_name = full_name
            u.position = position
            u.mobile_phone = mobile_phone
            u.inner_phone = inner_phone
            u.email = email
            if birth_date:
                u.birth_date = birth_date
            else:
                u.birth_date = None
            u.skype = skype

            db.session.add(u)
            db.session.flush()
            if photo:
                p = u.photo = u.photo or File.create(name='photo.png', module='users', entity=u)
                p.makedir()
                p.update_hash()
                image.thumbnail(photo, width = 100, height = 100, fill = image.COVER).save(p.get_path(sufix="thumbnail"))
                image.resize(photo).save(p.get_path())
            db.session.commit()
        return u

    def get_permissions(self):
        return set([permission.name for permission in self.permissions]).union(
            set([permission.name for role in self.roles for permission in role.permissions])
        )

    def has_role(self, role):
        return role in self.roles

    @property
    def age(self):
        today, born = date.today(), self.birth_date
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    def to_json(self):
        return user_schema.dump(self)


class PasswordRestore(db.Model):
    __tablename__ = 'password_restore'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    token = db.Column(db.String(64))
    is_active = db.Column(db.Boolean, default=True)
    datetime = db.Column(db.DateTime, default=datetime.now)

    author = db.relationship("User", backref="password_restore")

    def __repr__(self):
        return "<PasswordRestore {token}>".format(token=self.token)

    @classmethod
    def add_token(cls, user):
        token = ''.join(str(uuid1()).split('-'))
        pass_restore = PasswordRestore(author_id=user.id, token=token)
        db.session.add(pass_restore)
        db.session.commit()
        return token

    @classmethod
    def is_valid_token(cls, token):
        expiration = datetime.now() - timedelta(days=1)
        restore_pass = cls.query.filter(PasswordRestore.token == token,
                                   PasswordRestore.is_active == True,
                                   PasswordRestore.datetime >= expiration).first()
        return restore_pass

    @classmethod
    def deactivation_token(cls, token_obj):
        tokens = cls.query.filter(PasswordRestore.author_id == token_obj.author_id).all()
        for token in tokens:
            token.is_active = False
        db.session.commit()
