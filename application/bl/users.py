import ldap3
from flask import current_app

from application import ldap, db, sms_service
from application.models.user import User
from application.models.department import Department
from application.utils.datagen import generate_password, generate_inner_phone
from application.models.file import File
from application.utils import image

class DataProcessingError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


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


def create_user(login, name, surname, email, mobile_phone,
                department, groups, birth_date, skype, photo):
    password = generate_password()
    inner_phone = generate_inner_phone(current_app.config['INNER_PHONE_DIAPASON_BEGIN'],
                                       current_app.config['INNER_PHONE_DIAPASON_END'])
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

    if not _add_user_to_local_db(login, name, surname, email, department, photo,
                                 mobile_phone, inner_phone, birth_date, skype):
        raise DataProcessingError('Произошла ошибка при добавлении пользователя в локальную базу данных')

    if not _add_user_to_ldap(ldap_user_attr, groups):
        db.session.rollback()
        raise DataProcessingError('Произошла ошибка при добавлении пользователя в каталог LDAP')
    else:
        db.session.commit()

    if not sms_service.send_password(mobile_phone.strip('+'), login, password):
        raise DataProcessingError('Произошла ошибка при отправлении запроса на сообщение '
                                  'с логином и паролем пользователя')


def _add_user_to_ldap(user_attr, groups):
    try:
        result = ldap.add_user(attributes=user_attr)
        result &= ldap.add_user_to_groups(user=user_attr['cn'], groups=groups)
        return result
    except:
        return False


def _add_user_to_local_db(login, name, surname, email, department, photo,
                          mobile_phone, inner_phone, birth_date, skype):
    try:
        user = User()
        user.login = login
        user.full_name = "{0} {1}".format(name, surname)
        user.mobile_phone = mobile_phone
        user.inner_phone = inner_phone
        user.email = email
        user.department = Department.get_by_name(department)
        user.birth_date = birth_date
        user.skype = skype

        db.session.add(user)
        db.session.flush()

        p = user.photo = File.create(name='photo.png', module='users', entity=user)
        p.makedir()
        p.update_hash()
        image.thumbnail(photo, width=100, height=100, fill=image.COVER).save(p.get_path(sufix="thumbnail"))
        image.resize(photo).save(p.get_path())
        return True
    except:
        return False


def update_user(id, full_name, position, department, photo,
                email, mobile_phone, inner_phone, birth_date, skype):
    old_login = User.get_by_id(id).login
    ldap_user_attr = {
        'mobile': mobile_phone,
        'telephoneNumber': inner_phone,
        'displayName': full_name,
        'mail': email
    }

    if not _edit_user_at_local_db(id, full_name, position, department, photo, email, mobile_phone, inner_phone, birth_date, skype):
        raise DataProcessingError('Произошла ошибка при обновлении пользователя в локальной базе данных')

    if not _edit_user_at_ldap(old_login, ldap_user_attr):
        db.session.rollback()
        raise DataProcessingError('Произошла ошибка при обновлении пользователя в каталоге LDAP')
    else:
        db.session.commit()


def _edit_user_at_local_db(id, full_name, position, department, photo,
                           email, mobile_phone, inner_phone, birth_date, skype):
    try:
        User.edit_user(
            uid=id,
            full_name=full_name,
            position=position,
            email=email,
            inner_phone=inner_phone,
            mobile_phone=mobile_phone,
            birth_date=birth_date,
            skype=skype,
            photo=photo
        )
        User.add_user2dep(
            dep_id=Department.get_by_name(department).id,
            user_id=id
        )
        return True
    except:
        return False


def _edit_user_at_ldap(user, user_attr):
    try:
        result = ldap.modify_user(user, user_attr)
        return result
    except:
        return False