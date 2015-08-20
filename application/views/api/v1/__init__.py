from flask import render_template

from application import Module
from application.utils import auth

__author__ = 'newbie'

api_v1 = Module('api_v1', __name__, url_prefix='/api/v1')

@api_v1.before_request
def before_request():
    user = auth.service.get_user()
    if not user.is_admin:
        return render_template('403.html')

from . import users
from . import news
from . import comments
