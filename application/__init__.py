from application.models.user import User
from application.utils.auth.middleware import AuthMiddleware

from flask import Flask, g
import os
from application.db import db, redis
from application.ldap import ldap
from application.config import config
from application.module import Module
from application.utils.session import Session
from application.utils.auth.service import get_user
from application.views import *
from application.models import *


templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')


def create_app(config_name):
    app = Flask(__name__, template_folder=templates_dir, static_folder=static_folder)
    app.config.from_object(config[config_name])
    app.wsgi_app = AuthMiddleware(app.wsgi_app)

    db.init_app(app)
    redis.init_app(app)
    ldap.init_app(app)

    from application import models

    for _module in Module.get_all():
        app.register_blueprint(_module)

    # for rule in app.url_map.iter_rules():
    #     print(rule, rule.methods)


    @app.context_processor
    def inject_user():
        return dict(current_user=get_user())

    return app

