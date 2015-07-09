#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, request
from flask.ext.sqlalchemy import SQLAlchemy
from application.config import config
from application.module import Module
from application.utils.session import Session

__author__ = 's-tar'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = '{type}://{username}:{password}@{host}/{db}?charset=utf8'.format(**config['db'])
db = SQLAlchemy(app)

@app.before_request
def before_req():
    setattr(request, 'session', Session(request.environ['beaker.session']))

from application.modules import *

for module in Module.get_all():
    app.register_blueprint(module)


def print_routes():
    for rule in app.url_map.iter_rules():
        print(rule, rule.methods)

# print_routes()