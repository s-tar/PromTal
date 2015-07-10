#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from beaker.middleware import SessionMiddleware
from application import app
from application.config import config

__author__ = 's-tar'

app.wsgi_app = SessionMiddleware(app.wsgi_app, config['session'])

if __name__ == '__main__':
    app.run(host='192.168.1.2', port=3000, debug=True)