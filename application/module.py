#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Blueprint
import application

__author__ = 's-tar'


class Module(Blueprint):
    __all = []

    def __init__(self, *args, **kwargs):
        Blueprint.__init__(self, *args, **kwargs)
        self.__all.append(self)

    def post(self, rule, methods=[], **options):
        def wrap(f):
            return application.app.route(rule, methods=['POST'], **options)(f)
        return wrap

    def get(self, rule, methods=[], **options):
        def wrap(f):
            return application.app.route(rule, methods=['GET'], **options)(f)
        return wrap

    def delete(self, rule, methods=[], **options):
        def wrap(f):
            return application.app.route(rule, methods=['DELETE'], **options)(f)
        return wrap

    def put(self, rule, methods=[], **options):
        def wrap(f):
            return application.app.route(rule, methods=['PUT'], **options)(f)
        return wrap

    @classmethod
    def get_all(cls):
        return cls.__all