import ldap3
from flask import flash

from application import ldap, db
from application.models.user import User


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


def update_user(login, full_name, email, mobile_phone, inner_phone, birth_date, photo, skype):
    ldap_user_attr = {
        'mobile': mobile_phone,
        'telephoneNumber': inner_phone,
        'displayName': full_name,
        'mail': email
    }

    if not _edit_user_at_local_db(login, full_name, email, mobile_phone, inner_phone, birth_date, photo, skype):
        flash('Произошла ошибка при обновлении профиля в локальной базе данных', 'error')
        return False
    flash('Ваш профиль был успешно обновлен в локальной базе данных', 'info')

    if not _edit_user_at_ldap(login, ldap_user_attr):
        flash('Произошла ошибка при обновлении профиля в каталоге LDAP', 'error')
        return False
    flash('Ваш профиль был успешно обновлен в каталоге LDAP', 'info')

    return True


def _edit_user_at_local_db(login, full_name, email, mobile_phone, inner_phone, birth_date, photo, skype):
    try:
        user = User.get_by_login(login)
        user.full_name = full_name
        user.email = email
        user.mobile_phone = mobile_phone
        user.inner_phone = inner_phone
        user.skype = skype
        user.birth_date = birth_date if birth_date else user.birth_date
        user.photo = photo if photo else user.photo
        db.session.add(user)
        db.session.commit()
        return True
    except:
        return False


def _edit_user_at_ldap(user, user_attr):
    try:
        result = ldap.modify_user(user, user_attr)
        return result
    except:
        return False
