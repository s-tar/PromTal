from sqlalchemy.orm import class_mapper


class Mixin:
    @classmethod
    def get(cls, id):
        return cls.query.filter(cls.id == id).first()

    @classmethod
    def all(cls):
        return cls.query.order_by(cls.datetime.desc()).all()

    def as_dict(self):
        d = {}
        for c in self.__table__.columns:
            val = getattr(self, c.name)
            d[c.name] = str(val) if val is not None else ''
        return d

    def stringify(self):
        _key = [self.__table__.name]
        for f in class_mapper(self.__class__).primary_key:
            _key.append(str(getattr(self, f.name)))
        return '.'.join(_key)

    def stringify(self):
        _key = [self.__table__.name]
        for f in class_mapper(self.__class__).primary_key:
            _key.append(str(getattr(self, f.name)))
        return '.'.join(_key)