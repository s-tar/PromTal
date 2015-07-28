from application import ldap, db
from application.utils.datagen import generate_password, generate_inner_phone
from application.models.user import User


# TODO add exception processing
def add_user_data_to_db(data):
    data.update({
        'password': generate_password(),
        'inner_phone': str(generate_inner_phone({user.inner_phone for user in User.query.all()}))
    })

    ldap.add_user(user=data['login'], attributes=data)
    ldap.add_user_to_groups(user=data['login'], groups=data['groups'])

    user = User(login=data['login'],
                full_name=data['name']+' '+data['surname'],
                mobile_phone=data['mobile_phone'],
                inner_phone=data['inner_phone'],
                email=data['email'])
    db.session.add(user)
    db.session.commit()
