import pickle
from application import redis
from application.models.user import User
from application.utils.auth.user import User as AuthUser
from flask import request, g
from application.ldap import ldap


def get_user():
    if not g.get('user'):
        sid = request.cookies.get('sid', None)
        session = redis.get(sid)
        uid = None
        if session is not None:
            session = pickle.loads(session)
            uid = session.get('user', {}).get('id', None)
        g.user = User.get_by_id(uid) or AuthUser()
    return g.user


def login(login, password):
    if ldap.bind_user(login, password):
        sid = request.cookies.get('sid', None)
        user = User.get_by_login(login)
        uid = user and user.id or None
        if sid and uid:
            session = {'user': {'id': uid}}
            redis.set(sid, pickle.dumps(session))
            return True
    return False


def logout():
    sid = request.cookies.get('sid', None)
    session = redis.get(sid)
    if session is not None:
        session = pickle.loads(session)
        user = session.get('user', None)
        if user:
            user['id'] = None
            redis.set(sid, pickle.dumps(session))


