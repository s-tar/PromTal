from flask import current_app

from application import ldap, db
from application.utils.datagen import generate_password, generate_inner_phone
from application.models.user import User


# TODO add exception processing
def add_user_data_to_db(data):
    password = generate_password()
    inner_phone = generate_inner_phone({user.inner_phone for user in User.query.all()},
                                       current_app.config['INNER_PHONE_DIAPASON_BEGIN'],
                                       current_app.config['INNER_PHONE_DIAPASON_END'])
    data.update({
        'password': password,
        'inner_phone': inner_phone
    })

    _add_to_ldap(data)
    _add_to_local_db(data)
    # TODO send password with sms
    # smsserv.send_message(data['phone_number'], data['password'])


def _add_to_ldap(data):
    ldap.add_user(user=data['login'], attributes=data)
    ldap.add_user_to_groups(user=data['login'], groups=data['groups'])


def _add_to_local_db(data):
    user = User(login=data['login'],
                full_name="{0} {1}".format(data['name'], data['surname']),
                mobile_phone=data['mobile_phone'],
                inner_phone=data['inner_phone'],
                email=data['email'])
    db.session.add(user)
    db.session.commit()
