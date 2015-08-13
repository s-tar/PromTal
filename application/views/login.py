from flask import render_template, redirect, request, url_for
from flask.json import jsonify

from application import Module
from application.utils.validator import Validator
from application.utils import auth


module = Module('login', __name__, url_prefix='/login')


@module.get("/")
def login():
    return render_template('login.html')


@module.post("/")
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


@module.route("/logout")
def logout():
    auth.service.logout()
    return redirect(url_for('login.login'))
