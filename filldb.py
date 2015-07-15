import ldap3

from application import db, ldap, create_app
from application.models.user import User


def get_users_objects(connection, config):
    connection.search(search_base=config['LDAP_BASE_DN'],
                      search_filter=config['LDAP_USER_OBJECT_FILTER'],
                      search_scope=ldap3.SUBTREE,
                      attributes=ldap3.ALL_ATTRIBUTES)
    for user_object in connection.response:
        yield user_object['attributes']


def fill_db(config):
    print("Start filling DB ...")
    print("Create connection to LDAP server ...")
    ldap_conn = ldap.bind()
    print("Connection to LDAP server has been created successfully.")

    print("Start retrieving users' data from LDAP server ...")
    for user_object in get_users_objects(ldap_conn, config):
        user = User(login=user_object.get('cn', [''])[0],
                    full_name=user_object.get('displayName', [''])[0],
                    mobile_phone=user_object.get('mobile', [''])[0],
                    inner_phone=user_object.get('telephoneNumber', [''])[0],
                    email=user_object.get('email', [''])[0])
        db.session.add(user)
    db.session.commit()
    print("DB has been filled successfully.")

if __name__ == '__main__':
    app = create_app('default')
    fill_db(app.config)
