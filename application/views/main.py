import pickle
from application import redis
from application.utils import auth
from flask import request, render_template, redirect
from flask.json import jsonify

from application.utils.validator import Validator
from application.module import Module
from application.models.user import PasswordRestore, User


main = Module('main', __name__)


# @main.get("/")
# def index():
#     return render_template('index.html')


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