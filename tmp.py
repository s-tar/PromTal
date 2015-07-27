from application.models.user import User
from application.models.group import Group
from application import create_app
from application.utils.datagen import generate_inner_number

if __name__ == '__main__':
    app = create_app('default')
    with app.app_context():
        users = Group.query.all()
        print({user for user in users})
        # print(generate_inner_number({user.inner_phone for user in users}))
