from flask import request, render_template
from application.module import Module

main = Module('main', __name__)


@main.get("/")
def index():
    return render_template('index.html')


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


@main.route("/login")
def login():
    return render_template('login/login.html')


@main.route("/restore")
def restore():
    return render_template('login/restore.html')
