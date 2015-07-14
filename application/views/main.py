from flask import request, render_template
from application import app

@app.route("/")
def main():
    return render_template('main.html')


@app.route("/session")
@app.route("/session/<text>")
def session_check(text=None):
    s = request.session
    if text:
        s.text = text

    return "This is session check page.<br/>" \
           "Session text: %s" % s.text

@app.route("/profile")
def profile():
    return render_template('profile/profile.html')

@app.route("/login")
def login():
    return render_template('login/login.html')

@app.route("/restore")
def restore():
    return render_template('login/restore.html')