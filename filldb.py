import logging
import ldap3

from application import db, ldap, create_app
from application.models.user import User

logging.basicConfig(format='%(message)s', level=logging.INFO)


def get_users_objects(connection, config):
    connection.search(search_base=config['LDAP_BASE_DN'],
                      search_filter=config['LDAP_USER_OBJECT_FILTER'] % '*',
                      search_scope=ldap3.SUBTREE,
                      attributes=config['LDAP_USER_FIELDS'])
    for user_object in connection.response:
        yield user_object['attributes']


def fill_db(config):
    logging.info("Start filling DB ...")
    logging.info("Create connection to LDAP server ...")
    ldap_conn = ldap.bind()
    logging.info("Connection to LDAP server has been created successfully.")

    logging.info("Start retrieving users' data from LDAP server ...")
    for user_object in get_users_objects(ldap_conn, config):
        user = User(login=user_object.get('cn', [''])[0],
                    full_name=user_object.get('displayName', [''])[0],
                    mobile_phone=user_object.get('mobile', [''])[0],
                    inner_phone=user_object.get('telephoneNumber', [''])[0],
                    email=user_object.get('mail', [''])[0])
        db.session.add(user)
    db.session.commit()
    logging.info("DB has been filled successfully.")

if __name__ == '__main__':
    app = create_app('default')
    with app.app_context():
        fill_db(app.config)
