from datetime import datetime, date, timedelta
import os

from flask import Flask, render_template
from flask_bootstrap import Bootstrap

from application.db import db, redis
from application.ldap import ldap
from application.config import config
from application.module import Module
from application.utils.session import Session
from application.utils.auth.service import get_user
from application.utils.auth.middleware import AuthMiddleware
from application.views import *
from application.models import *


templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
files_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')


def create_app(config_name):
    app = Flask(__name__, template_folder=templates_dir, static_folder=static_folder)
    app.config.from_object(config[config_name])
    app.wsgi_app = AuthMiddleware(app.wsgi_app)

    Bootstrap(app)
    db.init_app(app)
    redis.init_app(app)
    ldap.init_app(app)

    from application import models

    for _module in Module.get_all():
        app.register_blueprint(_module)

    # for rule in app.url_map.iter_rules():
    #     print(rule, rule.methods)

    @app.template_filter('datetime')
    def format_datetime(value, time=True):
        time_str = "в %s" % value.strftime('%H:%M') if time else ''
        date_str = ''
        if value.date() == datetime.today().date():
            date_str = "Сегодня"
        elif value.date() == date.today() - timedelta(1):
            date_str = "Вчера"
        else:
            date_str = value.strftime('%d.%m.%y')
        return ' '.join((date_str, time_str))

        if format == 'full':
            format="EEEE, d. MMMM y 'at' HH:mm"
        elif format == 'medium':
            format="EE dd.MM.y HH:mm"
        return babel.format_datetime(value, format)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.context_processor
    def inject_user():
        return dict(current_user=get_user())

    return app

