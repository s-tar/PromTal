import os

from flask import Flask, request
from beaker.middleware import SessionMiddleware

from application.db import db
from application.ldap import ldap
from application.config import config
from application.module import Module
from application.utils.session import Session
from application.views import *


templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')


def create_app(config_name):
    app = Flask(__name__, template_folder=templates_dir, static_folder=static_folder)
    app.config.from_object(config[config_name])
    app.wsgi_app = SessionMiddleware(app.wsgi_app, config[config_name].session)

    db.init_app(app)
    ldap.init_app(app)

    from application import models

    for _module in Module.get_all():
        app.register_blueprint(_module)

    for rule in app.url_map.iter_rules():
        print(rule, rule.methods)

    @app.before_request
    def before_req():
        setattr(request, 'session', Session(request.environ['beaker.session']))

    return app
