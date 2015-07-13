from ldap3 import Connection, SUBTREE, ALL_ATTRIBUTES
import re

# from models.user import User
# from portal import db


LDAP_HOST = 'ldap.uaprom'
BASE = "ou=People,dc=uaprom,dc=net"
DN = "cn={}," + BASE
USER = 'ldc'
PASSWORD = 'ldc'


def phone_number_formatter(phone_number):
    ph_n_len = len(phone_number) if len(phone_number) <= 15 else len(phone_number.split('/')[0])
    return phone_number.replace('-', '')[:ph_n_len]


def get_info_from_ldap(host, user, password, dn):
    with Connection(host, dn.format(user), password) as connection:
        connection.search(search_base=BASE,
                          search_filter='(mobile=*)',
                          search_scope=SUBTREE,
                          attributes=ALL_ATTRIBUTES)
        for r in connection.response:
            yield r['attributes']


def fill_db():
    for entry in get_info_from_ldap(LDAP_HOST, USER, PASSWORD, DN):

        # user = User(
        #     login=entry['cn'],
        #     full_name=entry['displayName'],
        #     mobile_phone=entry['mobile'],
        #     inner_phone=entry['telephoneNumber'],
        #     email=entry['mail'],
        # )
        # db.session.add(user)
        # db.session.commit()

        print("{full_name}, tel:{mobile_phone}, login:{login}, email:{email}, iptel:{inner_phone}".format(
            login=entry.get('cn', [None]).pop(),
            full_name=entry.get('displayName', [None]).pop(),
            mobile_phone=phone_number_formatter(entry.get('mobile', [None]).pop()),
            inner_phone=entry.get('telephoneNumber', [None]).pop(),
            email=entry.get('mail', [None]).pop(),
        ))

fill_db()
