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


@user.post('/edit_profile')
def edit_profile_post():
    current_user = auth.service.get_user()
    v = Validator(request.form)
    v.field('full_name').required()
    v.field('email').email().required()
    file = request.files["file"]
    if bool(file.filename):
        try:
            name, name_s = save_user_fotos(file, current_user, avatar=True)
        except NotImage:
            v.add_error('file', 'Это не картинка')
    if v.is_valid():
        full_name = request.form.get("full_name")
        birth_date = datetime.strptime(request.form.get("birth_date"), "%d.%m.%Y")
        mobile_phone = request.form.get("mobile_phone")
        inner_phone = request.form.get("inner_phone")
        email = request.form.get("email")
        skype = request.form.get("skype")
        photo = name or None
        photo_s = name_s or None
        User.edit_user(current_user.id,
                       full_name=full_name,
                       mobile_phone=mobile_phone,
                       inner_phone=inner_phone,
                       email=email,
                       birth_date=birth_date,
                       skype=skype,
                       photo=photo,
                       photo_s=photo_s)
        return jsonify({"status": "ok"})
    return jsonify({"status": "fail",
                    "errors": v.errors})


@user.get("/edit_profile")
def edit_profile():
    return render_template('profile/edit_profile.html')


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


@user.get("/log_out")
def log_out():
    auth.service.logout()
    return redirect(url_for('user.login'))


@user.get("/restore")
def restore():
    return render_template('login/restore.html')


@user.post('/restore')
def restore_post():
    v = Validator(request.form)
    v.field('email').email().required()
    if v.is_valid():
        email = request.form.get("email")
        user = User.get_by_email(email)
        if user:
            token = PasswordRestore.add_token(user)
            send_mail_restore_pass(email, token)
        return jsonify({"status": "ok"})
    return jsonify({"status": "fail",
                    "errors": v.errors})


@user.get("/restore_pass/<token>")
def restore_pass(token):
    pass_restore = PasswordRestore.is_valid_token(token)
    if not pass_restore:
        abort(404)
    return render_template('login/new_pass.html', token=pass_restore.token)


@user.get("/new_pass")
def new_pass():
    return render_template('login/new_pass.html')


@user.post('/new_pass')
def new_pass_post():
    v = Validator(request.form)
    v.field('password_1').required()
    v.field('password_2').required()
    v.field('password_2').equal(v.field('password_1'))
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


@user.get("/edit_pass")
def edit_pass():
    return render_template('login/edit_pass.html')


@user.post('/edit_pass')
def edit_pass_post():
    current_user = auth.service.get_user()
    v = Validator(request.form)
    v.field('password_old').required()
    v.field('password_1').required()
    v.field('password_2').required()
    v.field('password_2').equal(v.field('password_1'))
    if v.is_valid():
        old_password = request.form.get("password_old")
        new_password = request.form.get("password_1")
        modify_password(current_user.login, old_password, new_password)
        return jsonify({"status": "ok"})
    return jsonify({"status": "fail",
                    "errors": v.errors})
