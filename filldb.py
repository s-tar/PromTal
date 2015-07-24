import logging
import sys
import ldap3

from application import db, ldap, create_app
from application.models.user import User
from application.models.group import Group


logging.basicConfig(format='%(message)s', level=logging.INFO)


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
    elif sys.argv[1] == 'groups':
        for group_attr in ldap.get_all_groups():
            group = Group(name=group_attr.get('cn', [''])[0])
            db.session.add(group)
    db.session.commit()
    logging.info("DB has been filled successfully.")

if __name__ == '__main__':
    app = create_app('default')
    with app.app_context():
        fill_db()
