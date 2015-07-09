#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from application.utils.immutable import imdict

__author__ = 's-tar'


config = imdict({
    'files':{
        'path':'./files'
    },
    'session': {
        'session.type': 'file',
        'session.cookie_expires': True,
        'session.data_dir': './tmp/session',
        'session.auto': True
    },
    'db': {
        'type': 'mysql',
        'host': "localhost",
        'db': 'project_kate',
        'port': 3306,
        'username': 'root',
        'password': '',
    },
    'sn': {
        'vk': {
            'app_id': 3775380,
            'app_secret': '6skSVjVfzcCJLCdx9NUg'
        },
        'fb': {
            'app_id': '276442509075653',
            'app_secret': '931b421a32c44cbcebdccf3063bdb649'
        }
    }
})