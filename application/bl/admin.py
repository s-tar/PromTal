from flask import flash

from application import ldap, db, sms_service
from application.utils.datagen import generate_password, generate_inner_phone
from application.models.user import User


def create_user(login, name, surname, email, mobile_phone, department, groups):
    password = generate_password()
    inner_phone = generate_inner_phone()
    ldap_user_attr = {
        'cn': login,
        'userPassword': password,
        'displayName': "{0} {1}".format(name, surname),
        'givenName':  name,
        'sn': surname,
        'mail': email,
        'mobile': mobile_phone,
        'telephoneNumber': inner_phone,
        'departmentNumber': department,
    }

    if not _add_user_to_local_db(login, name, surname, email, department, mobile_phone, inner_phone):
        flash('Произошла ошибка при добавлении пользователя в локальную базу данных')
        return False
    flash('Пользователь был успешно добавлен в локальную базу данных')

    if not _add_user_to_ldap(login, ldap_user_attr, groups):
        user = User.get_by_login(login)
        db.session.delete(user)
        db.session.commit()
        flash('Произошла ошибка при добавлении пользователя в LDAP')
        return False
    flash('Пользователь был успешно добавлен в LDAP')

    if sms_service.send_password(mobile_phone.strip('+'), login, password):
        flash('Запрос на сообщение с логином и пароле пользователя был отослан SMS-сервису')
    else:
        flash('Произошла ошибка при отправлении запроса на сообщение '
              'с логином и паролем пользователя SMS-сервису')

    return True


def _add_user_to_ldap(user, user_attr, groups):
    try:
        ldap.add_user(user=user, attributes=user_attr)
        ldap.add_user_to_groups(user=user, groups=groups)
        return True
    except Exception:
        return False


def _add_user_to_local_db(login, name, surname, email, department, mobile_phone, inner_phone):
    try:
        user = User(login=login,
                    full_name="{0} {1}".format(name, surname),
                    mobile_phone=mobile_phone,
                    inner_phone=inner_phone,
                    email=email)
        db.session.add(user)
        db.session.commit()
        return True
    except Exception:
        return False
