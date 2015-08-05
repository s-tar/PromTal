from application import Module, ldap, db
from application.utils.validator import Validator
from application.utils import auth
from application.utils.image_processing.user_foto import save_user_fotos, NotImage
from flask import request, render_template, redirect, url_for, abort
from flask.json import jsonify
from werkzeug.utils import secure_filename
from application.mail_sender import send_mail_restore_pass
from application.models.user import User, PasswordRestore
from datetime import datetime
from application.bl.user import restore_password, modify_password

user = Module('user', __name__, url_prefix='/user')


@user.get("/profile")
def profile():
    current_user = auth.service.get_user()
    return render_template('profile/profile.html', user=current_user)


@user.get("/profile/<user_id>")
def profile_id(user_id):
    user = User.get_by_id(user_id)
    if not user:
        abort(404)
    return render_template('profile/profile.html', user=user)


@user.get("/profile/edit")
def edit_profile():
    return render_template('profile/edit_profile.html')


@user.post('/profile/edit')
def edit_profile_post():
    current_user = auth.service.get_user()
    data = dict(request.form)
    data["file"] = request.files["file"]

    v = Validator(data)
    v.field('full_name').required()
    v.field('email').email().required()
    v.field('birth_date').datetime(format="%d.%m.%Y")
    v.field('file').image()
    if v.is_valid():
        full_name = request.form.get("full_name")
        birth_date = request.form.get("birth_date")
        if birth_date:
            birth_date = datetime.strptime(birth_date, "%d.%m.%Y")
        mobile_phone = request.form.get("mobile_phone")
        inner_phone = request.form.get("inner_phone")
        email = request.form.get("email")
        skype = request.form.get("skype")

        User.edit_user(current_user.id,
                       full_name=full_name,
                       mobile_phone=mobile_phone,
                       inner_phone=inner_phone,
                       email=email,
                       birth_date=birth_date,
                       skype=skype,
                       photo=v.valid_data.file)
        return jsonify({"status": "ok"})
    return jsonify({"status": "fail",
                    "errors": v.errors})


@user.get("/login")
def login():
    return render_template('login/login.html')


@user.post('/login')
def login_post():
    v = Validator(request.form)
    v.field("login").required()
    v.field("password").required()
    if v.is_valid():
        login = v.valid_data.login
        password = v.valid_data.password
        if auth.service.login(login, password):
            return jsonify({"status": "ok"})
        else:
            v.add_error('login', 'Логин или пароль не верен', 'wrong_login_or_password')
    return jsonify({"status": "fail",
                    "errors": v.errors})


@user.route("/logout")
def log_out():
    auth.service.logout()
    return redirect(url_for('user.login'))


@user.route("/password/restore")
def restore():
    return render_template('login/restore.html')


@user.post('/password/restore')
def restore_post():
    v = Validator(request.form)
    v.field('email').required().email()
    if v.is_valid():
        email = request.form.get("email")
        user = User.get_by_email(email)
        if user:
            token = PasswordRestore.add_token(user)
            send_mail_restore_pass(email, token)
        return jsonify({"status": "ok"})
    return jsonify({"status": "fail",
                    "errors": v.errors})


@user.route("/password/restore/<token>")
def restore_pass(token):
    pass_restore = PasswordRestore.is_valid_token(token)
    if not pass_restore:
        abort(404)
    return render_template('login/new_pass.html', token=pass_restore.token)


@user.route("/password/new")
def new_pass():
    return render_template('login/new_pass.html')


@user.post('/password/new')
def new_pass_post():
    v = Validator(request.form)
    v.field('password_1').required()
    v.field('password_2').required()
    v.field('password_2').equal(v.field('password_1'), message="Повторый пароль неверный")
    if v.is_valid():
        restore_pass = PasswordRestore.is_valid_token(request.form.get("token"))
        if not restore_pass:
            abort(404)
        new_password = request.form.get("password_1")
        restore_password(restore_pass.author.login, new_password)
        PasswordRestore.deactivation_token(restore_pass)
        return jsonify({"status": "ok"})
    return jsonify({"status": "fail",
                    "errors": v.errors})


@user.route("/password/change")
def edit_pass():
    return render_template('login/edit_pass.html')


@user.post('/password/change')
def edit_pass_post():
    current_user = auth.service.get_user()
    v = Validator(request.form)
    v.field('password_old').required()
    v.field('password_1').required()
    v.field('password_2').required()
    v.field('password_2').equal(v.field('password_1'), message="Повторый пароль неверный")
    if v.is_valid():
        old_password = request.form.get("password_old")
        new_password = request.form.get("password_1")
        try:
            modify_password(current_user.login, old_password, new_password)
        except:
            v.field('password_old').old_password()
            return jsonify({"status": "fail", "errors": v.errors})
        return jsonify({"status": "ok"})
    return jsonify({"status": "fail",
                    "errors": v.errors})
