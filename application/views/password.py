from flask import render_template, redirect, request, url_for, abort
from flask.json import jsonify

from application import Module
from application.utils.validator import Validator
from application.mail_sender import send_mail_restore_pass
from application.models.user import User, PasswordRestore
from application.bl.users import restore_password


module = Module('password', __name__, url_prefix='/password')


@module.get("/restore")
def restore():
    return render_template('password/restore.html')


@module.post('/restore')
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


@module.get("/restore/<token>")
def restore_pass(token):
    pass_restore = PasswordRestore.is_valid_token(token)
    if not pass_restore:
        abort(404)
    return render_template('password/new_pass.html', token=pass_restore.token)


@module.get("/new")
def new_pass():
    return render_template('password/new_pass.html')


@module.post('/new')
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