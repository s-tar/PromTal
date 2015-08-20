from flask import request, render_template, redirect, url_for, abort
from collections import defaultdict

from application import Module, ldap, db
from application.utils import auth
from application.models.department import Department
from application.models.user import User
from application.utils.datatables_sqlalchemy.datatables import row2dict


module = Module('company_structure', __name__, url_prefix='/structure')


@module.before_request
def before_request():
    user = auth.service.get_user()
    if not user.is_authorized():
        return redirect(url_for('login.login'))


def get_departments(parent_id=None):
    dep_list = []
    departments = db.session.query(Department).filter_by(parent_id=parent_id).all()
    for dep in departments:
        dep_dict = row2dict(dep)
        if dep_dict["user_id"] != 'None':
            user = User.get_by_id(dep_dict["user_id"])
            dep_dict["user"] = row2dict(user)
        print(dep_dict)
        dep_dict['dep_list'] = get_departments(dep.id)
        dep_list.append(dep_dict)
    if len(departments):
        return dep_list
    else:
        return None

@module.get("/show")
def show_structure():
    departments = defaultdict(list)
    for department in Department.all():
        departments[department.parent_id].append(department)
    return render_template('company_structure/show.html', departments=departments)