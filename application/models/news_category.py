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