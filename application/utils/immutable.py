#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 's-tar'


class xset(set):
    def __freeze__(self):
        return frozenset(self)


class xlist(list):
    def __freeze__(self):
        return tuple(self)


class imdict(dict):
    def __hash__(self):
        return id(self)

    def _immutable(self, *args, **kws):
        raise TypeError('object is immutable')

    __setitem__ = _immutable
    __delitem__ = _immutable
    clear = _immutable
    update = _immutable
    setdefault = _immutable
    pop = _immutable
    popitem = _immutable


class xdict(dict):
    def __freeze__(self):
        return imdict(self)