import pickle
from application import redis
from flask import request, render_template, redirect, url_for
from flask.json import jsonify

from application.utils import auth
from application.utils.validator import Validator
from application.module import Module
from application.models.user import User


main = Module('main', __name__)


@main.before_request
def before_requets():
    user = auth.service.get_user()
    if not user.is_authorized():
        return redirect(url_for('login.login'))


@main.get("/force_login")
def session_check(text=None):
    sid = request.cookies.get('sid', None)
    user = User.get_by_login('qwe')
    uid = user and user.id or None
    if sid and uid:
        session = {'user': {'id': uid}}
        redis.set(sid, pickle.dumps(session))
        return True


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

# @main.route('/parse_asl')
# def parser_asf():
#     with open('application/static/images/smiles/tango/MSNTango.asl', 'r') as f:
#         for line in f.readlines():
#             parts = line.split(' "')
#             if len(parts) > 2:
#                 file = parts[1].split('"')[0].strip('",')
#                 text = parts[2].strip('",').strip('-125, ').split()
#                 if len(file) > 1:
#                     print('"/static/images/smiles/tango/'+file+'":', '["'+'", "'.join(text)+'"],')