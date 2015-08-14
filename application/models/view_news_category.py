from application.db import db


class ViewNewsCategory(db.Model):
    __tablename__ = 'view_news_category'
    news_category_id = db.Column(db.Integer, primary_key=True)
    news_category_name = db.Column(db.String(255))
    count_news = db.Column(db.Integer)
    count_views = db.Column(db.Integer)
    count_votes = db.Column(db.Integer)
    count_comments = db.Column(db.Integer)

    def __repr__(self):
        return "<ViewNewsCategory {name}>".format(name=self.news_category_name)