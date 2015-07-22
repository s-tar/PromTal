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