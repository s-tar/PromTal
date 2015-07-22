from application import Module, ldap, db
from application.utils.validator import Validator
from application.utils import auth
from flask import request, render_template, redirect, url_for
from flask.json import jsonify
from application.mail_sender import send_mail_restore_pass
from application.models.user import User, PasswordRestore
from datetime import datetime


user = Module('user', __name__, url_prefix='/user')


@user.get("/profile")
def profile():
    return render_template('profile/profile.html')


@user.get("/profile/<user_id>")
def profile_id(user_id):
    user = User.get_by_id(user_id)
    if not user:
        return render_template('404.html')
    return render_template('profile/profile_id.html', user=user)


@user.get("/edit_profile")
def edit_profile():
    return render_template('profile/edit_profile.html')


@user.route("/login")
def login():
    return render_template('login/login.html')


@user.route("/log_out")
def log_out():
    auth.service.logout()
    return redirect(url_for('user.login'))


@user.route("/restore")
def restore():
    return render_template('login/restore.html')


@user.route("/restore_pass/<token>")
def restore_pass(token):
    pass_restore = PasswordRestore.is_valid_token(token)
    if not pass_restore:
        return render_template('404.html')
    return render_template('login/new_pass.html', token=pass_restore.token)


@user.route("/new_pass")
def new_pass():
    return render_template('login/new_pass.html')


@user.route("/edit_pass")
def edit_pass():
    return render_template('login/edit_pass.html')


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

    return jsonify(
        {"status": "fail",
         "errors": v.errors}
    )


@user.post('/registration')
def registration():
    v = Validator(request.form)
    v.field("login").required()
    v.field("password").required()
    v.field("password").required().length(min=5, message="Длина пароля не менее %(min)d символов")
    if v.data.get("password") != v.data.get("repassword"):
        v.add_error('password', 'Пароли не совпадают', 'wrong_repassword')

    if v.is_valid():
        return jsonify({"status": "ok"})

    return jsonify(
        {"status": "fail",
         "errors": v.errors}
    )


@user.post('/restore')
def restore_post():
    v = Validator(request.form)

    # Валидация полей
    
    if v.is_valid():
        email = request.form.get("email")
        user = User.get_by_email(email)
        if user:
            token = PasswordRestore.add_token(user)
            send_mail_restore_pass(email, token)
        return jsonify({"status": "ok"})
    return jsonify(
        {"status": "fail",
         "errors": v.errors}
    )


@user.post('/edit_profile')
def edit_profile_post():
    current_user = auth.service.get_user()
    v = Validator(request.form)

    if v.is_valid():
        full_name = request.form.get("full_name")
        birth_date = datetime.strptime(request.form.get("birth_date"), "%d.%m.%Y")
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
                       skype=skype)

        return jsonify({"status": "ok"})
    return jsonify(
        {"status": "fail",
         "errors": v.errors}
    )


@user.post('/new_pass')
def new_pass_post():
    v = Validator(request.form)

    # Валидация паролей

    if v.is_valid():
        restore_pass = PasswordRestore.is_valid_token(request.form.get("token"))
        #token_obj = PasswordRestore.is_valid_token("44a8c92e2d1b11e58f9228d24470c3ec") # не удалять пока
        #if token_obj:# не удалять пока
        password_1 = request.form.get("password_1")
        password_2 = request.form.get("password_2")

        # Сохранение нового пароля
        # print("\n\n\n")
        # print(restore_pass.id)
        # print(restore_pass.author)

        # Changing user password
        result = ldap.change_password(restore_pass.author.login, password_1)

        #PasswordRestore.deactivation_token(token_obj) # не удалять пока
        return jsonify({"status": "ok"})
    return jsonify(
        {"status": "fail",
         "errors": v.errors}
    )

@user.post('/edit_pass')
def edit_pass_post():
    v = Validator(request.form)

    # Валидация паролей

    if v.is_valid():
        password_old = request.form.get("password_old")
        password_1 = request.form.get("password_1")
        password_2 = request.form.get("password_2")

        # Сохранение нового пароля
        print("\n\n\n", password_old, password_1, password_2)

        return jsonify({"status": "ok"})
    return jsonify(
        {"status": "fail",
         "errors": v.errors}
    )