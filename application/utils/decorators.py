from functools import wraps
from werkzeug.exceptions import abort

from application.utils import auth


def requires_permissions(*permissions):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            user = auth.service.get_user()
            if not user.is_authorized():
                return abort(403)
            if not user.is_admin:
                if not set.intersection(user.get_permissions(), set(permissions)):
                    return abort(403)
            return f(*args, **kwargs)
        return wrapped
    return wrapper