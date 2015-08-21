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
        dep = db.session.query(User).filter_by(parent_id=None).first()
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


@module.post('/profile/edit')
def edit_profile_post():
    current_user = auth.service.get_user()
    data = dict(request.form)
    data["file"] = request.files["file"]

    v = Validator(data)
    v.field('full_name').required()
    v.field('email').required().email()
    v.field('mobile_phone').required().phone_number()
    v.field('department').required()
    v.field('birth_date').datetime(format="%d.%m.%Y")
    v.field('file').image()
    if v.is_valid():
        data = {
            'id': current_user.id,
            'login': current_user.login,
            'full_name': v.valid_data.full_name,
            'position': v.valid_data.position,
            'mobile_phone': v.valid_data.mobile_phone,
            'inner_phone': v.valid_data.inner_phone,
            'department': v.valid_data.department,
            'email': v.valid_data.email,
            'skype': v.valid_data.skype,
            'photo': v.valid_data.file,
            'birth_date': v.valid_data.birth_date
        }

        try:
            update_user(**data)
            return jsonify({"status": "ok"})
        except DataProcessingError as e:
            return jsonify({'status': 'failOnProcess',
                            'error': e.value})

    return jsonify({"status": "fail",
                    "errors": v.errors})


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


@widget('user.birthdays')
def birthdays():
    users = User.get_birthday()
    return render_template('user/birthdays.html',  **{'users': users})


@widget('user.new.members')
def birthdays():
    users = User.get_new()
    return render_template('user/new_members.html',  **{'users': users})
