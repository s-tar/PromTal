from flask import request, current_app

from . import api_v1

from application.db import db
from application.models.user import User
from application.models.news import News
from application.models.comment import Comment
from application.models.serializers.user import user_schema
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
        'objects': [x.to_json().data for x in p.items],
    }


@api_v1.get('/users/<int:id>/')
@json()
def get_user(id):
    user = User.query.get_or_404(id)
    return user.to_json().data


@api_v1.delete('/users/<int:id>/')
@json()
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return {}, 204


@api_v1.put('/users/<int:id>/')
@json()
def edit_user(id):
    user = User.query.get_or_404(id)

    result = user_schema.load(request.get_json())

    if result.errors:
        return result.errors, 400

    for field, value in result.data.items():
        setattr(user, field, value)

    db.session.commit()
    return user.to_json().data, 200


@api_v1.post('/users/')
@json()
def create_user():
    result = user_schema.load(request.get_json())

    if result.errors:
        return result.errors, 400

    user = User(**result.data)

    db.session.add(user)
    db.session.commit()
    return user.to_json().data, 200


@api_v1.get('/users/<int:id>/news/')
@json()
def get_user_news(id):
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', current_app.config['PROFILE_NEWS_PER_PAGE'],
                                    type=int), current_app.config['PROFILE_NEWS_PER_PAGE'])
    user = User.query.get_or_404(id)
    user_news = (
        News.query
        .filter(News.author == user)
        .order_by(News.datetime.desc())
    )
    p = user_news.paginate(page, per_page)

    return {
        'paginator': {
            'page': page,
            'pages': p.pages,
        },
        'objects': [x.to_json().data for x in p.items],
    }


@api_v1.get('/users/<int:id>/comments/')
@json()
def get_user_comments(id):
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', current_app.config['PROFILE_COMMENTS_PER_PAGE'],
                                    type=int), current_app.config['PROFILE_COMMENTS_PER_PAGE'])
    user = User.query.get_or_404(id)
    user_comments = (
        Comment.query
        .filter(Comment.author == user)
        .order_by(Comment.datetime.desc())
    )
    p = user_comments.paginate(page, per_page)

    return {
        'paginator': {
            'page': page,
            'pages': p.pages,
        },
        'objects': [x.to_json().data for x in p.items],
    }
