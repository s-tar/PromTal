from application import ldap


def restore_password(login, new_password):
    return ldap.restore_password(login, new_password)


def modify_password(login, old_password, new_password):
    return ldap.modify_password(login, old_password, new_password)