import ldap3
from flask import current_app


class LDAPException(RuntimeError):
    message = None

    def __init__(self, message):
        self.message = message

    def __str__(self):
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
        app.config.setdefault('LDAP_USER_FIELDS', [])
        app.config.setdefault('LDAP_USER_OBJECT_FILTER', '(objectClass=*)')
        app.config.setdefault('LDAP_USER_PASSWORD_FIELD', 'userPassword')
        app.config.setdefault('LDAP_LOGIN_VIEW', 'login')


        for option in ['USERNAME', 'PASSWORD', 'BASE_DN']:
            if app.config['LDAP_{0}'.format(option)] is None:
                raise LDAPException('LDAP_{0} cannot be None!'.format(option))

    def initialize(self):
        try:
            server = ldap3.Server('{0}://{1}:{2}'.format(
                current_app.config['LDAP_SCHEMA'],
                current_app.config['LDAP_HOST'],
                current_app.config['LDAP_PORT']))
            return server
        except ldap3.LDAPExceptionError as e:
            raise LDAPException(self.error(e))

    def bind(self):
        server = self.initialize()
        try:
            conn = ldap3.Connection(
                server=server,
                user=current_app.config['LDAP_USERNAME'],
                password=current_app.config['LDAP_PASSWORD'],
                authentication=ldap3.SIMPLE)
            conn.bind()
            return conn
        except ldap3.LDAPExceptionError as e:
            raise LDAPException(self.error(e))

    def bind_user(self, username, password):
        user_dn = self.get_object_details(username, dn_only=True)
        print(user_dn)
        if user_dn is None:
            return
        try:
            server = self.initialize()
            conn = ldap3.Connection(
                server=server,
                user=user_dn,
                password=password,
                authentication=ldap3.SIMPLE)
            return conn.bind()
        except ldap3.LDAPExceptionError:
            return

    def get_object_details(self, username, dn_only=False):
        if dn_only:
            return current_app.config['LDAP_USER_OBJECT_DN'].format(username) + \
                   ',' + current_app.config['LDAP_BASE_DN']

    def change_password(self, username, new_password):
        try:
            conn = self.bind()
            user_dn = self.get_object_details(username, dn_only=True)
            result = conn.modify(
                dn=user_dn,
                changes={current_app.config['LDAP_USER_PASSWORD_FIELD']: [(ldap3.MODIFY_REPLACE, new_password)]}
            )
            return result
        except ldap3.LDAPExceptionError as e:
            raise LDAPException(self.error(e))


    @staticmethod
    def error(e):
        if 'desc' in dict(e.message):
            return dict(e.message)['desc']
        else:
            return e[1]
