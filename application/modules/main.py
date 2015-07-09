#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import request
from application import app

__author__ = 's-tar'

@app.route("/")
def index():
    return "This is index page."


@app.route("/session")
@app.route("/session/<text>")
def session_check(text=None):
    s = request.session
    if text:
        s.text = text

    return "This is session check page.<br/>" \
           "Session text: %s" % s.text