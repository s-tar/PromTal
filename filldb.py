import logging
import sys

from application import db, ldap, create_app
from application.models.user import User


logging.basicConfig(format='%(message)s', level=logging.DEBUG)


def fill_db():
    logging.info("Start filling DB ...")
    if sys.argv[1] == 'users':
        for user_attr in ldap.get_all_users():
            user = User(login=user_attr.get('cn', [''])[0],
                        full_name=user_attr.get('displayName', [''])[0],
                        mobile_phone=user_attr.get('mobile', [''])[0],
                        inner_phone=user_attr.get('telephoneNumber', [''])[0],
                        email=user_attr.get('mail', [''])[0])
            db.session.add(user)
            db.session.commit()
    else:
        logging.error("Wrong argument passed.")
    logging.info("DB has been filled successfully.")

if __name__ == '__main__':
    app = create_app('default')
    with app.app_context():
        fill_db()
