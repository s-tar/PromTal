from application.utils import auth
from flask import request, render_template, redirect
from flask.json import jsonify

from application.utils.validator import Validator
from application.module import Module
from application.models.user import PasswordRestore


main = Module('main', __name__)


# @main.get("/")
# def index():
#     return render_template('index.html')


@main.get("/session")
@main.get("/session/<text>")
def session_check(text=None):
    s = request.session
    if text:
        s.text = text

    return "This is session check page.<br/>" \
           "Session text: %s" % s.text


@main.get("/profile")
def profile():
    return render_template('profile/profile.html')


@main.get("/edit_profile")
def edit_profile():
    return render_template('profile/edit_profile.html')


@main.route("/login")
def login():
    return render_template('login/login.html')


@main.route("/log_out")
def log_out():
    auth.service.logout()
    return redirect("/login")


@main.route("/restore")
def restore():
    return render_template('login/restore.html')


@main.route("/restore_pass/<token>")
def restore_pass(token):
    pass_restore = PasswordRestore.is_valid_token(token)
    if not pass_restore:
        return render_template('404.html')
    return render_template('login/new_pass.html', token=pass_restore.token)


@main.route("/new_pass")
def new_pass():
    return render_template('login/new_pass.html')


@main.route("/message/<msg>")
def message(msg):
    return render_template('message.html', msg=msg)


@main.route("/demo_form", methods=['POST'])
def test():
    v = Validator(request.form)
    v.fields('email').email()
    v.field('first_name').required()
    v.field('text').required().length(max=6)
    if v.is_valid():
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'fail',
            'errors': v.errors})
