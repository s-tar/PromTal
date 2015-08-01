import application
from application import db
from application.config import Config as config
from application.models.mixin import Mixin
import hashlib
import uuid
import os
from sqlalchemy.orm import class_mapper

root = os.path.dirname(os.path.abspath(os.path.join(__file__, '../')))


class File(db.Model, Mixin):
    __tablename__ = 'file'
    id = db.Column(db.Integer, primary_key=True)
    module = db.Column(db.String(255))
    entity = db.Column(db.String(255))
    name = db.Column(db.String(255))
    extension = db.Column(db.String(255))
    hash = db.Column(db.String(255))
    external_link = db.Column(db.String(255))
    visible = db.Column(db.Boolean(create_constraint=False), default=True)
    order = db. Column(db.Integer, default=1)

    @classmethod
    def get(cls, name=None, module=None, entity=None):
        if name or module or entity:
            query = cls.query
            if entity:
                if isinstance(entity, list):
                    query = query.filter(File.entity.in_((File.stringify_entity(e) for e in entity)))
                else:
                    query = query.filter(File.entity == File.stringify_entity(entity))
            if module: query = query.filter(File.module == module)
            if name:
                parts = name.rsplit('.', 1)
                query = query.filter(File.name == parts[0])
                if len(parts) > 1:
                    query = query.filter(File.extension == parts[1])
            query = query.order_by(File.order, File.id)
            return query.all()
        return []

    @classmethod
    def create(cls, name, module=None, entity=None, external_link=None):
        name = name.strip("/")
        name_parts = name.split('.')

        new_file = File()
        new_file.name = name_parts[0]
        new_file.module = module
        new_file.entity = File.stringify_entity(entity)
        new_file.extension = name_parts[-1] if len(name_parts) > 1 else None

        new_file.update_hash()
        new_file.external_link = external_link

        db.session.add(new_file)
        db.session.flush()

        return new_file

    def __get_path(self, sufix=None, hash=False):
        path = []
        if self.module: path.append(self.module)
        if self.entity: path.append(self.entity)
        path = os.path.normpath(os.path.join('/'.join(path), self.get_name(sufix, hash)))
        return path

    def is_local(self):
        return self.external_link is None

    def get_name(self, sufix=None, hash=False):
        name = []
        name.append('id'+str(self.id))
        if sufix: name.append(sufix)
        if hash: name.append('_'+self.hash+'_')
        if self.extension: name.append(self.extension)
        return '.'.join(name)

    def update_hash(self):
        self.hash = str(uuid.uuid4()).replace('-', '')

    def get_path(self, sufix=None):
        if self.external_link:
            return None
        path = self.__get_path(sufix)
        return os.path.join(application.files_folder, path)

    def get_url(self, sufix=None):
        if self.external_link:
            return self.external_link
        path = self.__get_path(sufix, hash=True)
        return '/'.join(['', config.files['url'], path])

    def makedir(self):
        if not self.external_link:
            path = os.path.dirname(self.get_path())
            if not os.path.exists(path):
                os.makedirs(path)

    def remove_files(self):
        path, name = self.get_path().rsplit(os.sep, 1)
        name = self.name.split('/')[-1]+'.id'+str(self.id)
        if os.path.exists(path):
            for f in os.listdir(path):
                if not os.path.isdir(f) and f.startswith(name):
                    os.remove(os.path.join(path, f))

    @staticmethod
    def stringify_entity(entity):
        if isinstance(entity, db.Model):
            _key = [entity.__table__.name]
            for f in class_mapper(entity.__class__).primary_key:
                _key.append(str(getattr(entity, f.name)))
            return '.'.join(_key)
        return str(entity)