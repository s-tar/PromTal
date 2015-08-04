from flask import current_app, flash

from application import ldap, db, sms_service
from application.utils.datagen import generate_password, generate_inner_phone
from application.models.user import User


def create_user(data):
    password = generate_password()
    inner_phone = generate_inner_phone({user.inner_phone for user in User.query.all()},
                                       current_app.config['INNER_PHONE_DIAPASON_BEGIN'],
                                       current_app.config['INNER_PHONE_DIAPASON_END'])
    data.update({'inner_phone': inner_phone})
    ldap_user_attr = {
        'cn': data['login'],
        'userPassword': password,
        'displayName': "{0} {1}".format(data['name'], data['surname']),
        'givenName':  data['name'],
        'sn': data['surname'],
        'mail': data['email'],
        'mobile': data['mobile_phone'],
        'telephoneNumber': data['inner_phone'],
        'departmentNumber': data['department'],
    }

    if _add_to_ldap(ldap_user_attr, data['groups']):
        flash('Пользователь был успешно добавлен в LDAP')
    else:
        flash('Произошла ошибка при добавлении пользователя в LDAP')
        return False

    if _add_to_local_db(data):
        flash('Пользователь был успешно добавлен в локальную базу данных')
    else:
        flash('Произошла ошибка при добавлении пользователя в локальную базу данных')
        return False

    if sms_service.send_password(data['mobile_phone'].strip('+'), data['login'], password):
        flash('Сообщение с логином и паролем было успешно отослано пользователю')
    else:
        flash('Произошла ошибка при отправлении сообщения с логином и паролем пользователю')

    return True


def _add_to_ldap(ldap_user_attr, ldap_groups):
    try:
        ldap.add_user(user=ldap_user_attr['cn'], attributes=ldap_user_attr)
        ldap.add_user_to_groups(user=ldap_user_attr['cn'], groups=ldap_groups)
        return True
    except Exception:
        return False


def _add_to_local_db(data):
    try:
        user = User(login=data['login'],
                    full_name="{0} {1}".format(data['name'], data['surname']),
                    mobile_phone=data['mobile_phone'],
                    inner_phone=data['inner_phone'],
                    email=data['email'])
        db.session.add(user)
        db.session.commit()
    except Exception:
        return False
