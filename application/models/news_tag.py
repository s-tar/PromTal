from application.db import db


class NewsTag(db.Model):
    __tablename__ = 'news_tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

    @classmethod
    def get_tags(cls, tags=None):
        if tags is not None:
            return cls.query.filter(NewsTag.name.in_(tags)).all()
        else:
            return cls.query.all()