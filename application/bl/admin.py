from application import ldap, db
from application.utils.datagen import generate_password, generate_inner_phone
from application.models.user import User


def add_user_data_to_db(data):
    password = generate_password()
    inner_phone = generate_inner_phone({user.inner_phone for user in User.query.all()})
