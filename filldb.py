import logging
import sys

from application import db, ldap, create_app
from application.models.user import User
from application.models.department import Department


logger = logging.getLogger('filldb')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)s: %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)
logger.addHandler(handler)


def logging_wrapper(func):
    def wrapper(*args, **kwargs):
        logger.info("Start filling DB ...")
        func(*args, **kwargs)
        logger.info("DB has been filled successfully.")

    return wrapper


@logging_wrapper
def add_all_users():
    for user_attr in ldap.get_all_users():
        user = User(login=user_attr.get('cn', [''])[0],
                    full_name=user_attr.get('displayName', [''])[0],
                    mobile_phone=user_attr.get('mobile', [''])[0],
                    inner_phone=user_attr.get('telephoneNumber', [''])[0],
                    email=user_attr.get('mail', [''])[0])
        db.session.add(user)
    db.session.commit()


@logging_wrapper
def add_all_departments():
    for department_name in ldap.get_all_departments():
        department = Department(name=department_name)
        db.session.add(department)
    db.session.commit()


@logging_wrapper
def add_departments_members():
    for department_name, usernames in ldap.get_department_info().items():
        department = Department.get_by_name(department_name)
        for user in User.query.filter(User.login.in_(usernames)):
            user.department = department
    db.session.commit()


COMMANDS = {
    'users': add_all_users,
    'departments': add_all_departments,
    'departments-members': add_departments_members
}


def fill_db():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        logger.error("Wrong argument passed.")
    else:
        COMMANDS[sys.argv[1]]()

if __name__ == '__main__':
    app = create_app('default')
    with app.app_context():
        fill_db()
