from application import create_app, ldap


app = create_app('default')
with app.app_context():
    all_users = 0
    all_departments = 0
    departments_info = ldap.get_department_info()
    for department, users in departments_info.items():
        all_users += len(users)
        all_departments += 1

        print(department, ' : ', ", ".join(users))

    print(all_departments, all_users)