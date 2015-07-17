import pickle
from application import redis
from application.models.user import User
from flask import request, g


def get_user():
    if not g.get('user'):
        sid = request.cookies.get('sid', None)
        session = redis.get(sid)
        uid = None
        if session is not None:
            session = pickle.loads(session)
            uid = session.get('user', {}).get('id', None)
        g.user = User.get_by_id(uid)
    return g.user


def login(user):
    sid = request.cookies.get('sid', None)
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
