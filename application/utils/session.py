#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 's-tar'


class Session():
    def __init__(self, data):
        self.__dict__.update({'_Session__data': data})

    def __getattr__(self, item):
        if hasattr(self.__data, item):
            return getattr(self.__data, item)

        return self.__data.get(item, None)

    def __setattr__(self, key, value):
        self.__data[key] = value