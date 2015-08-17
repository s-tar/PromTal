from application.db import db
from application.models.mixin import Mixin


class NewsCategory(db.Model, Mixin):
    __tablename__ = 'news_category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    parent_id = db. Column(db.Integer, db.ForeignKey('news_category.id'), nullable=True)

    parent = db.relationship('NewsCategory', remote_side=[id],  backref="subcategories", lazy='joined')

    @classmethod
    def get_root(cls):
        return cls.query.filter(cls.parent_id == None).all()

    @classmethod
    def add(cls, name):
        cat = NewsCategory(name=name)
        db.session.add(cat)
        db.session.commit()

    @classmethod
    def get_by_id(cls, uid):
        return cls.query.filter_by(id=uid).first()

    @classmethod
    def rename(cls, uid, new_name):
        cat = cls.query.filter_by(id=uid).first()
        cat.name = new_name
        db.session.add(cat)
        db.session.commit()

    @classmethod
    def delete(cls, uid):
        cls.query.filter_by(id=uid).delete()
        db.session.commit()

    @classmethod
    def get_all(cls):
        return cls.query.order_by(NewsCategory.name).all()