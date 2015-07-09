#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from application import app

__author__ = 's-tar'


@app.route("/admin")
def admin():
    return "This is admin page."

