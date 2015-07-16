from flask.ext.redis import FlaskRedis
from flask.ext.sqlalchemy import SQLAlchemy


db = SQLAlchemy()
redis = FlaskRedis()