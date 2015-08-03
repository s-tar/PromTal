from application import Module

__author__ = 'newbie'

api_v1 = Module('api_v1', __name__, url_prefix='/api/v1')

from . import users
from . import news
from . import comments