from application.db import db


class ViewNews(db.Model):
    __tablename__ = 'view_news'
    news_id = db.Column(db.Integer, primary_key=True)
    news_title = db.Column(db.String(255))
    users_id = db.Column(db.Integer)
    user_full_name = db.Column(db.String(64))
    news_category_id = db.Column(db.Integer)
    news_category_name = db.Column(db.String(255))

    def __repr__(self):
        return "<ViewNews {name}>".format(name=self.news_title)