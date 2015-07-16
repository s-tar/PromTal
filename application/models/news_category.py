from application.db import db


class NewsCategory(db.Model):
    __tablename__ = 'news_category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    parent_id = db. Column(db.Integer, db.ForeignKey('news_category.id'), nullable=True)

    parent = db.relationship('NewsCategory', remote_side=[id],  backref="subcategories")
