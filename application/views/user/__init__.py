from application import Module
from application.utils.validator import Validator
from flask import request, render_template
from flask.json import jsonify

user = Module('user', __name__, url_prefix='/user')


@user.post('/login')
def login_post():
    v = Validator(request.form)
    v.field("login").required()
    v.field("password").required()
    if v.is_valid():
        return jsonify({"status": "ok"})

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
