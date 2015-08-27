from flask import request, render_template, abort, redirect, url_for
from flask.json import jsonify

from application import Module
from application.utils.validator import Validator
from application.utils import auth
from application.utils.widget import widget
from application.models.user import User
from application.models.department import Department
from application.db import db
from application.bl.users import modify_password, PasswordError, DataProcessingError, update_user
from application.utils.datatables_sqlalchemy.datatables import ColumnDT, DataTables
from application.models.view_users4search import ViewUsers4Search

module = Module('user', __name__, url_prefix='/user')


@module.before_request
def before_request():
    user = auth.service.get_user()
    if not user.is_authorized():
        return redirect(url_for('login.login'))


@module.get("/profile")
@module.get("/profile/<int:user_id>")
def profile(user_id=None):
    user = auth.service.get_user() if user_id is None else User.get_by_id(user_id)
    if user is None:
        abort(404)
    user_department = Department.get_dep_if_user_head(user.id)
    count_users = ''
    if user_department:
        count_users = Department.count_users_in_dep_tree(user_department.id)
    if user.department_id:
        head_user = Department.get_head_user_in_dep_tree(user.department_id, user.id)
    else:
        dep = db.session.query(Department).filter_by(parent_id=None).first()
        head_user = Department.get_head_user_in_dep_tree(dep.id, user.id)
    return render_template('profile/profile.html', user=user,
                                                   user_department=user_department,
                                                   count_users=count_users,
                                                   head_user=head_user)


@module.get("/profile/edit")
def edit_profile():
    departments = Department.query.all()
    return render_template('profile/edit_profile.html',
                           departments={department.name for department in departments})


@module.route("/password/change")
def edit_pass():
    return render_template('profile/edit_pass.html')


@module.post('/password/change')
def edit_pass_post():
    current_user = auth.service.get_user()
    v = Validator(request.form)
    v.field('password_old').required()
    v.field('password_1').required()
    v.field('password_2').required()
    v.field('password_2').equal(v.field('password_1'), message="Повторный пароль неверный")
    if v.is_valid():
        old_password = request.form.get("password_old")
        new_password = request.form.get("password_1")
        try:
            modify_password(current_user.login, old_password, new_password)
        except PasswordError:
            v.add_error('password_old', 'Неверный пароль')
            return jsonify({"status": "fail", "errors": v.errors})
        return jsonify({"status": "ok"})
    return jsonify({"status": "fail",
                    "errors": v.errors})


@module.get('/users_search')
def users_search():
    return render_template('user/users_search.html')


@widget('user.birthdays')
def birthdays():
    users = User.get_birthday()
    return render_template('user/birthdays.html',  **{'users': users})


@widget('user.new.members')
def new_members():
    users = User.get_new()
    return render_template('user/new_members.html',  **{'users': users})


def _default_value_view(chain):
    if chain == 'None':
        return None
    return chain


def _empty(chain):
    return ''


@module.get('/users_search_json')
def users_search_json():
    columns = list()
    columns.append(ColumnDT('users_id', filter=_default_value_view))
    columns.append(ColumnDT('users_full_name', filter=_default_value_view))
    columns.append(ColumnDT('users_login', filter=_empty))
    columns.append(ColumnDT('users_email', filter=_empty))
    columns.append(ColumnDT('users_status', filter=_empty))
    columns.append(ColumnDT('users_mobile_phone', filter=_empty))
    columns.append(ColumnDT('users_inner_phone', filter=_empty))
    columns.append(ColumnDT('users_birth_date', filter=_empty))
    columns.append(ColumnDT('users_skype', filter=_empty))
    columns.append(ColumnDT('users_position', filter=_empty))
    columns.append(ColumnDT('department_name', filter=_default_value_view))
    columns.append(ColumnDT('photo_url', filter=_default_value_view))
    return jsonify(**DataTables(request, ViewUsers4Search, db.session.query(ViewUsers4Search), columns).output_result())
