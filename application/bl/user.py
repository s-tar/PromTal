import ldap3

from application import ldap


class PasswordError(LookupError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def restore_password(login, new_password):
    return ldap.restore_password(login, new_password)


def modify_password(login, old_password, new_password):
    try:
        return ldap.modify_password(login, old_password, new_password)
    except ldap3.LDAPBindError:
        raise PasswordError("wrong password has been passed.")
