import os
from beaker.middleware import SessionMiddleware
from flask import Flask, request
from flask.ext.sqlalchemy import SQLAlchemy
from application.config import config
from application.module import Module
from application.utils.session import Session

templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

app = Flask(__name__, template_folder=templates_dir, static_folder=static_folder)
app.wsgi_app = SessionMiddleware(app.wsgi_app, config['session'])

app.config['SQLALCHEMY_DATABASE_URI'] = '{type}://{username}:{password}@{host}/{db}?charset=utf8'.format(**config['db'])
db = SQLAlchemy(app)

@app.before_request
def before_req():
    setattr(request, 'session', Session(request.environ['beaker.session']))

from application.views import *

for module in Module.get_all():
    app.register_blueprint(module)


def print_routes():
    for rule in app.url_map.iter_rules():
        print(rule, rule.methods)

#print_routes()