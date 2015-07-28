from flask import request, current_app

from . import api_v1

from application.db import db
from application.models.user import User
from application.views.api.decorators import json


@api_v1.get('/users/')
@json()
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', current_app.config['ADMIN_USERS_PER_PAGE'],
                                    type=int), current_app.config['ADMIN_USERS_PER_PAGE'])

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
        'objects': [x.to_json() for x in p.items]
    }


@api_v1.get('/users/<int:id>')
@json()
def get_user(id):
    user = (
        User.query.get_or_404(id)
    )
    return user.to_json()


@api_v1.delete('/users/<int:id>')
@json()
def delete_user(id):
    user = (
        User.query.get(id)
    )
    db.session.delete(user)
    db.session.commit()
    return {}, 204


@api_v1.put('/users/<int:id>')
@json()
def edit_user(id):
    name = request.form.get('name')
    email = request.form.get('email')
    full_name = request.form.get('full_name')
    user = (
        User.query.get(id)
    )
    user.name = name
    user.email = email
    user.full_name = full_name

    db.session.add(user)
    db.session.commit()
    return {}, 200


@api_v1.post('/users/')
@json()
def create_user():
    name = request.form.get('name')
    email = request.form.get('email')
    full_name = request.form.get('full_name')
    print(email, full_name)
    user = User(login='111',
                        full_name='11112',
                        mobile_phone='121212',
                        inner_phone='2123124',
                        email='343423')
    print(user, user.id)
    db.session.add(user)
    db.session.commit()
    return user.to_json(), 200
