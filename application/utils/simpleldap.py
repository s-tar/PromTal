import hashlib

import ldap3
from ldap3.extend.standard.modifyPassword import ModifyPassword

from flask import current_app


# TODO hash password
# TODO add method for customizing filters
class LDAP(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    @staticmethod
    def init_app(app):
        #  general configuration
        app.config.setdefault('LDAP_HOST', 'localhost')
        app.config.setdefault('LDAP_PORT', 389)
        app.config.setdefault('LDAP_SCHEMA', 'ldap')
        app.config.setdefault('LDAP_USERNAME', None)
        app.config.setdefault('LDAP_PASSWORD', None)
        app.config.setdefault('LDAP_BASE_DN', None)

        #  user object configuration
        app.config.setdefault('LDAP_USER_BASE_DN', None)
        app.config.setdefault('LDAP_USER_FIELDS', [])
        app.config.setdefault('LDAP_USER_OBJECT_FILTER', '(cn=%s)')
        app.config.setdefault('LDAP_USER_PASSWORD_FIELD', 'userPassword')

        # group object configuration
        app.config.setdefault('LDAP_GROUP_BASE_DN', None)
        app.config.setdefault('LDAP_GROUP_FIELDS', [])
        app.config.setdefault('LDAP_GROUP_OBJECT_FILTER', '(cn=%s)')
        app.config.setdefault('LDAP_GROUP_MEMBER_FIELD', 'member')

        app.config.setdefault('LDAP_LOGIN_VIEW', 'login')

        for option in ['USERNAME', 'PASSWORD', 'BASE_DN', 'GROUP_BASE_DN', 'USER_BASE_DN']:
            if app.config['LDAP_{0}'.format(option)] is None:
                raise ldap3.LDAPDefinitionError('LDAP_{0} cannot be None!'.format(option))

    def initialize(self):
        try:
            server = ldap3.Server('{0}://{1}:{2}'.format(
                current_app.config['LDAP_SCHEMA'],
                current_app.config['LDAP_HOST'],
                current_app.config['LDAP_PORT']))
            return server
        except ldap3.LDAPExceptionError as e:
            raise e  # TODO add appropriate processing

    def bind(self):
        try:
            server = self.initialize()
            conn = ldap3.Connection(server=server,
                                    user=current_app.config['LDAP_USERNAME'],
                                    password=current_app.config['LDAP_PASSWORD'],
                                    authentication=ldap3.SIMPLE)
            conn.bind()
            return conn
        except ldap3.LDAPExceptionError as e:
            return  # TODO add appropriate processing

    def bind_user(self, user, password, get_connection=False):
        user_dn = self.get_object_details(user=user, dn_only=True)
        if user_dn is None:
            return
        try:
            server = self.initialize()
            conn = ldap3.Connection(server=server,
                                    user=user_dn,
                                    password=password,
                                    authentication=ldap3.SIMPLE)
            conn.bind()
            if get_connection:
                return conn
            else:
                return conn.bound
        except ldap3.LDAPExceptionError:
            return  # TODO add appropriate processing

    def restore_password(self, user, new_password):
        try:
            conn = self.bind()
            user_dn = self.get_object_details(user=user, dn_only=True)
            conn.modify(dn=user_dn,
                        changes={
                            current_app.config['LDAP_USER_PASSWORD_FIELD']: [(ldap3.MODIFY_REPLACE, new_password)]
                        })
            conn.unbind()
        except ldap3.LDAPExceptionError as e:
            raise e  # TODO add appropriate processing

    def modify_password(self, user, old_password, new_password):
        try:
            conn = self.bind_user(user, old_password, get_connection=True)
            user_dn = self.get_object_details(user=user, dn_only=True)
            modification = ModifyPassword(conn, user_dn, old_password, new_password)
            modification.send()
            conn.unbind()
        except ldap3.LDAPExceptionError as e:
            raise e  # TODO add appropriate processing

    def add_user(self, userdata):
        try:
            conn = self.bind()
            conn.add(dn=userdata['dn'],
                     attributes={
                         'objectClass': ['puppetClient', 'top', 'inetOrgPerson'],  # TODO enable to choose in the admin page
                         'cn': userdata['login'],
                         'displayName': userdata['name'] + ' ' + userdata['surname'],
                         'givenName':  userdata['name'],
                         'sn': userdata['surname'],
                         'mail': userdata['email'],
                         'mobile': userdata['mobile_phone'],
                         'telephoneNumber': userdata['inner_phone'],
                         'departmentNumber': userdata['department'],
                         'puppetClass': ['workstation'],
                         'environment': ['workstation'],
                         'description': 'no description'
                     })
            result = conn.result
            conn.unbind()
            return result
        except ldap3.LDAPExceptionError as e:
            raise e  # TODO add appropriate processing

    def add_user_to_groups(self, user, groups):
        try:
            conn = self.bind()
            user_dn = self.get_object_details(user=user, dn_only=True)
            for group in groups:
                group_dn = self.get_object_details(group=group, dn_only=True)
                conn.modify(dn=group_dn,
                            changes={
                                current_app.config['LDAP_GROUP_MEMBER_FIELD']: [(ldap3.MODIFY_ADD, user_dn)]
                            })
            conn.unbind()
        except ldap3.LDAPExceptionError as e:
            raise e  # TODO add appropriate processing

    def get_user_groups(self, user):
        user_dn = self.get_object_details(user=user, dn_only=True)
        try:
            conn = self.bind()
            conn.search(search_base=current_app.config['LDAP_GROUP_BASE_DN'],
                        search_filter='(member=*)',  # TODO FILTER DOESN'T WORk
                        search_scope=ldap3.SUBTREE,
                        attributes=current_app.config['LDAP_GROUP_FIELDS'])
            for group in conn.response:
                yield group['attribute']
            conn.unbind()
        except ldap3.LDAPExceptionError as e:
            raise e  # TODO add appropriate processing

    def get_all_users(self):
        try:
            conn = self.bind()
            conn.search(search_base=current_app.config['LDAP_USER_BASE_DN'],
                        search_filter=current_app.config['LDAP_USER_OBJECT_FILTER'] % '*',  # TODO remove hard-code
                        search_scope=ldap3.SUBTREE,
                        attributes=current_app.config['LDAP_USER_FIELDS'])
            for entry in conn.response:
                yield entry['attributes']
            conn.unbind()
        except ldap3.LDAPExceptionError as e:
            raise e  # TODO add appropriate processing

    def get_all_groups(self):
        try:
            conn = self.bind()
            conn.search(search_base=current_app.config['LDAP_GROUP_BASE_DN'],
                        search_filter=current_app.config['LDAP_GROUP_OBJECT_FILTER'] % '*',  # TODO remove hard-code
                        search_scope=ldap3.SUBTREE,
                        attributes=current_app.config['LDAP_GROUP_FIELDS'])
            for entry in conn.response:
                yield entry['attributes']
            conn.unbind()
        except ldap3.LDAPExceptionError as e:
            raise e  # TODO add appropriate processing

    def get_object_details(self, user=None, group=None, dn_only=False):
        filter = None
        attributes = None
        if user is not None:
            if not dn_only:
                attributes = current_app.config['LDAP_USER_FIELDS']
            filter = current_app.config['LDAP_USER_OBJECT_FILTER'] % user  # TODO remove hard-code
        elif group is not None:
            if not dn_only:
                attributes = current_app.config['LDAP_GROUP_FIELDS']
            filter = current_app.config['LDAP_GROUP_OBJECT_FILTER'] % group  # TODO remove hard-code
        try:
            conn = self.bind()
            conn.search(search_base=current_app.config['LDAP_USER_BASE_DN'] if user
                        else current_app.config['LDAP_GROUP_BASE_DN'] if group
                        else current_app.config['LDAP_BASE_DN'],
                        search_filter=filter,
                        search_scope=ldap3.SUBTREE,
                        attributes=attributes)
            response = conn.response
            conn.unbind()
            if response:
                if dn_only:
                    return response[0]['dn']
                return {'dn': response[0]['dn'], 'attributes': response[0]['attributes']}
        except ldap3.LDAPExceptionError as e:
            raise e  # TODO add appropriate processing
