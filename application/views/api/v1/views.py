from flask import request
from flask.json import jsonify

from application import Module, config
from application.models.user import *

api_v1 = Module('api_v1', __name__, url_prefix='/api/v1')


@api_v1.get('/users/')
@jsonify
def get_users():
    def _jsonify(item):
        return {
            'id': item.id,
            'name': item.name,
            'email': item.email,
            'full_name': item.full_name,
            'login': item.login,
            'status': item.status,
            'roles': item.roles,
            'mobile_phone': item.mobile_phone,
            'inner_phone': item.inner_phone,
            'birth_date': item.birth_date,
            'avatar': item.avatar,
            'photo': item.photo,
            'skype': item.skype,
        }

    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', config['ADMIN_USERS_PER_PAGE'],
                                    type=int), config['ADMIN_USERS_PER_PAGE'])

    users = (
        User.query
        .order_by(User.full_name.desc())
    )
    p = users.paginate(page, per_page)

    return {
        'paginator': {
            'page': page,
            'pages': p.pages,
        },
        'objects': [_jsonify(x) for x in p.items]
    }
