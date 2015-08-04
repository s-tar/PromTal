import hashlib
import logging

import ldap3
from ldap3.extend.standard.modifyPassword import ModifyPassword

from flask import current_app


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
        server = ldap3.Server('{0}://{1}:{2}'.format(
            current_app.config['LDAP_SCHEMA'],
            current_app.config['LDAP_HOST'],
            current_app.config['LDAP_PORT']))
        return server

    def bind(self):
        server = self.initialize()
        conn = ldap3.Connection(server=server,
                                user=current_app.config['LDAP_USERNAME'],
                                password=current_app.config['LDAP_PASSWORD'],
                                authentication=ldap3.SIMPLE)
        conn.bind()
        return conn if conn.bound else None

    def bind_user(self, user, password, get_connection=False):
        user_dn = self.get_object_details(user=user, dn_only=True)
        if user_dn is None:
            return None
        server = self.initialize()
        h_password = hashlib.sha1(password.encode()).hexdigest()
        conn = ldap3.Connection(server=server,
                                user=user_dn,
                                password=h_password,
                                authentication=ldap3.SIMPLE)
        conn.bind()
        if get_connection:
            return conn
        bound = conn.bound
        conn.unbind()
        return bound

    def restore_password(self, user, new_password):
        conn = self.bind()
        user_dn = self.get_object_details(user=user, dn_only=True)
        h_new_password = hashlib.sha1(new_password.encode()).hexdigest()
        conn.modify(dn=user_dn,
                    changes={
                        current_app.config['LDAP_USER_PASSWORD_FIELD']: [(ldap3.MODIFY_REPLACE, h_new_password)]
                    })
        conn.unbind()

    def modify_password(self, user, old_password, new_password):
        conn = self.bind_user(user, old_password, get_connection=True)
        if not conn.bound:
            raise ldap3.LDAPBindError("user %s can not be bound" % user)
        user_dn = self.get_object_details(user=user, dn_only=True)
        if user_dn is None:
            return
        h_old_password = hashlib.sha1(old_password.encode()).hexdigest()
        h_new_password = hashlib.sha1(new_password.encode()).hexdigest()
        modification = ModifyPassword(conn, user_dn, h_old_password, h_new_password)
        modification.send()
        conn.unbind()

    # TODO test it
    def add_user(self,
                 user,
                 attributes,
                 object_classes=['puppetClient', 'top', 'inetOrgPerson']):
        conn = self.bind()
        conn.add(dn="cn={0},{1}".format(user, current_app.config['LDAP_USER_BASE_DN']),
                 object_class=object_classes,
                 attributes={
                     'cn': user,
                     'userPassword': hashlib.sha1(attributes['userPassword'].encode()).hexdigest(),
                     'displayName': attributes['displayName'],
                     'givenName':  attributes['givenName'],
                     'sn': attributes['sn'],
                     'mail': attributes['mail'],
                     'mobile': attributes['mobile'],
                     'telephoneNumber': attributes['telephoneNumber'],
                     'departmentNumber': attributes['departmentNumber'],
                     'puppetClass': ['workstation'],
                     'environment': ['workstation'],
                     'description': 'no description'
                 })
        result = conn.result
        conn.unbind()
        return result

    def add_user_to_groups(self, user, groups):
        conn = self.bind()
        user_dn = self.get_object_details(user=user, dn_only=True)
        if user_dn is None:
            return
        for group in groups:
            group_dn = self.get_object_details(group=group, dn_only=True)
            if group_dn is None:
                continue
            changes = {current_app.config['LDAP_GROUP_MEMBER_FIELD']: [(ldap3.MODIFY_ADD, user_dn)]}
            conn.modify(dn=group_dn,
                        changes=changes)
        conn.unbind()

    # TODO test it
    def modify_user(self, user, attributes):
        conn = self.bind()
        ldap_user = self.get_object_details(user=user)
        if ldap_user is None:
            return
        changes = {attr_name: {ldap3.MODIFY_REPLACE, attributes.get(attr_name, ldap_user[attr_name])}
                   for attr_name in attributes.keys()}
        conn.modify(dn=ldap_user['dn'], changes=changes)
        conn.unbind()

    def get_user_groups(self, user):
        user_dn = self.get_object_details(user=user, dn_only=True)
        if user_dn is None:
            return
        conn = self.bind()
        conn.search(search_base=current_app.config['LDAP_GROUP_BASE_DN'],
                    search_filter='(member={})'.format(user_dn),
                    search_scope=ldap3.SUBTREE,
                    attributes=current_app.config['LDAP_GROUP_FIELDS'])
        for group in conn.response:
            yield group['attribute']
        conn.unbind()

    def get_all_users(self):
        conn = self.bind()
        conn.search(search_base=current_app.config['LDAP_USER_BASE_DN'],
                    search_filter=current_app.config['LDAP_USER_OBJECT_FILTER'] % '*',  # TODO remove hard-code
                    search_scope=ldap3.SUBTREE,
                    attributes=current_app.config['LDAP_USER_FIELDS'])
        for entry in conn.response:
            yield entry['attributes']
        conn.unbind()

    def get_all_groups(self):
        conn = self.bind()
        conn.search(search_base=current_app.config['LDAP_GROUP_BASE_DN'],
                    search_filter=current_app.config['LDAP_GROUP_OBJECT_FILTER'] % '*',  # TODO remove hard-code
                    search_scope=ldap3.SUBTREE,
                    attributes=current_app.config['LDAP_GROUP_FIELDS'])
        for entry in conn.response:
            yield entry['attributes']
        conn.unbind()

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
