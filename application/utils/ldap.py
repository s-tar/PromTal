from functools import wraps

import ldap3
from flask import abort, current_app, g, make_response, redirect, url_for, request


class LDAPException(RuntimeError):
    message = None

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

    def __unicode__(self):
        return self.message


class LDAP(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    @staticmethod
    def init_app(app):
        app.config.setdefault('LDAP_HOST', 'localhost')
        app.config.setdefault('LDAP_PORT', 389)
        app.config.setdefault('LDAP_SCHEMA', 'ldap')
        app.config.setdefault('LDAP_USERNAME', None)
        app.config.setdefault('LDAP_PASSWORD', None)
        app.config.setdefault('LDAP_BASE_DN', None)
        app.config.setdefault('LDAP_OBJECTS_DN', 'distinguishedName')
        app.config.setdefault('LDAP_LOGIN_VIEW', 'login')

        for option in ['USERNAME', 'PASSWORD', 'BASE_DN']:
            if app.config['LDAP_{0}'.format(option)] is None:
                raise LDAPException('LDAP_{0} cannot be None!'.format(option))

    def initialize(self, user=None, password=None, authentication=None):
        server = ldap3.Server('{0}://{1}:{2}'.format(
                self.app.config['LDAP_SCHEMA'],
                self.app.config['LDAP_HOST'],
                self.app.config['LDAP_PORT']))
        try:
            conn = ldap3.Connection(
                server=server,
                user=user,
                password=password,
                authentication=authentication)
            return conn
        except ldap3.LDAPExceptionError as e:
            raise LDAPException(self.error(e))

    def bind(self):
        try:
            conn = self.initialize(
                self.app.config['LDAP_USERNAME'],
                self.app.config['LDAP_PASSWORD'],
                ldap3.SIMPLE
            )
            conn.bind()
            return conn
        except ldap3.LDAPExceptionError as e:
            raise LDAPException(self.error(e))

    def bind_user(self, username, password):
        user_dn = self.simple_formatter(current_app.config['LDAP_BASE_DN'],
                                        current_app.config['LDAP_OBJECTS_DN'],
                                        username)
        if user_dn is None:
            return
        try:
            conn = self.initialize(user_dn, password, ldap3.SIMPLE)
            return conn.bind()
        except ldap3.LDAPExceptionError:
            return

    # TODO Change simple_formatter to more flexible method
    @staticmethod
    def simple_formatter(base, dn, value):
        return '{dn}={value},{base}'.format(dn=dn, value=value, base=base)

    @staticmethod
    def login_require(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if g.user is None:
                return redirect(url_for(current_app.config['LDAP_LOGIN_VIEW'],
                                        next=request.path))
            return func(*args, **kwargs)

        return wrapped

    @staticmethod
    def error(e):
        if 'desc' in dict(e.message):
            return dict(e.message)['desc']
        else:
            return e[1]
