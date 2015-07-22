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


@main.route("/message/<msg>")
def message(msg):
    return render_template('message.html', msg=msg)


@main.route("/demo_form", methods=['POST'])
def test():
    v = Validator(request.form)
    v.fields('email').email()
    v.field('first_name').integer()
    v.field('text').required().length(max=6)
    v.field('image').image()
    if v.is_valid():
        return jsonify({'status': 'ok'})

    return jsonify({'status': 'fail',
            'errors': v.errors})
