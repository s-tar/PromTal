from functools import wraps
from application.utils import auth

__author__ = 'newbie'



def requires_permissions(*permissions):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            current_user = auth.service.get_user()
            if current_user.get_permissions() not in permissions:
                return error_response()
            return f(*args, **kwargs)
        return wrapped
    return wrapper