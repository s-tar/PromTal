from application import Module
from application.utils.validator import Validator
from application.utils import auth
from flask import request, render_template, redirect
from flask.json import jsonify
from application.mail_sender import send_mail_restore_pass
from application.models.user import User, PasswordRestore
from datetime import datetime

user = Module('user', __name__, url_prefix='/user')


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
    #v.field("email").email().required()
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
    print("\n\n\n", auth.service.get_user().id, "\n\n\n")
    v = Validator(request.form)
    if v.is_valid():
        full_name = request.form.get("full_name")
        birth_date = datetime.strptime(request.form.get("birth_date"), "%d.%m.%Y")
        mobile_phone = request.form.get("mobile_phone")
        inner_phone = request.form.get("inner_phone")
        email = request.form.get("email")
        skype = request.form.get("skype")
        User.edit_user(auth.service.get_user().id,
            full_name=full_name,
            mobile_phone=mobile_phone,
            inner_phone=inner_phone,
            email=email,
            birth_date=birth_date,
            skype=skype)
        #email = request.form.get("email")
        #user = User.get_by_email(email)
        #if user:
        #    token = PasswordRestore.add_token(user)
        #    send_mail_restore_pass(email, token)
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
        #token_obj = PasswordRestore.is_valid_token("44a8c92e2d1b11e58f9228d24470c3ec") # не удалять пока
        #if token_obj:# не удалять пока
        password_1 = request.form.get("password_1")
        password_2 = request.form.get("password_2")

        # Сохранение нового пароля

        #PasswordRestore.deactivation_token(token_obj) # не удалять пока
        return jsonify({"status": "ok"})
    return jsonify(
        {"status": "fail",
         "errors": v.errors}
    )