from application.models.file import File
from application.utils import image, auth
from flask import request, current_app, url_for, render_template
from flask.ext.sqlalchemy import BaseQuery
from sqlalchemy import func, desc

from . import api_v1

from application.db import db
from application.models.user import User
from application.models.news import News
from application.models.comment import Comment
from application.models.serializers.user import user_schema
from application.utils.validator import Validator
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
    user.status = User.STATUS_DELETED
    db.session.commit()
    return {}, 204


@api_v1.post('/users/')
@api_v1.put('/users/<int:id>/')
@json()
def save_user(id=None):

    data = dict()
    for key, value in request.form.items():
        data[key] = value

    data["file"] = request.files["file"]
    data['full_name'] = '{} {}'.format(request.form['name'], request.form['surname'])

    v = Validator(data)
    v.field('name').required()
    v.field('surname').required()
    v.field('file').image()
    v.field('inner_phone')
    v.field('email').required().email()
    v.field('login').required()
    v.field('department').required()
    v.field('groups')
    v.field('mobile_phone')
    v.field('skype')
    v.field('birth_date').datetime(format='%d.%m.%Y')

    print(v.valid_data.birth_date)
    already_used_login = User.get_by_login(data['login'])
    already_used_email = User.get_by_email(data['email'])

    user = User.query.get_or_404(id) if id else User()

    if already_used_login and already_used_login != user:
        v.add_error('login', 'Такой логин уже занят')
    if already_used_email and already_used_email != user:
        v.add_error('email', 'Такой email уже занят')

    if v.errors:
        return {'status': 'fail', 'errors': v.errors}, 200

    result = user_schema.load(data)

    for field, value in result.data.items():
        setattr(user, field, value)

    db.session.add(user)
    db.session.flush()

    if data["file"]:
        p = user.photo = user.photo or File.create(name='photo.png', module='users', entity=user)
        p.makedir()
        p.update_hash()
        image.thumbnail(data["file"], width=100, height=100, fill=image.COVER).save(p.get_path(sufix="thumbnail"))
        image.resize(data["file"]).save(p.get_path())
    db.session.commit()

    return {'status': 'ok', 'user_data': user.to_json().data}, 200


@api_v1.get('/users/<int:id>/news/')
@json()
def get_user_news(id):
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', current_app.config['PROFILE_NEWS_PER_PAGE'],
                                    type=int), current_app.config['PROFILE_NEWS_PER_PAGE'])
    user = User.query.get_or_404(id)
    user_news = (
        db.session.query(News.id, News.title, News.datetime)
        .filter(News.author == user)
        .order_by(News.datetime.desc())
    )
    p = BaseQuery.paginate(user_news, page, per_page)

    return {
        'paginator': {
            'page': page,
            'pages': p.pages,
        },
        'objects': [dict(zip(['news_id', 'news_title', 'created_date'], map(str, x))) for x in p.items],
    }


@api_v1.get('/users/<int:id>/comments-in-news/')
@json()
def get_user_comments_in_news(id):
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', current_app.config['PROFILE_COMMENTS_PER_PAGE'],
                                    type=int), current_app.config['PROFILE_COMMENTS_PER_PAGE'])
    user = User.query.get_or_404(id)
    user_comments_in_news = (
        db.session.query(News.id,
                         News.title,
                         func.count(Comment.id),
                         func.max(Comment.modify_datetime).label('last_modified'))
        .join(Comment, News.id == Comment.entity_id)
        .filter(Comment.author == user)
        .group_by(News.id)
        .order_by(desc('last_modified'))
    )
    p = BaseQuery.paginate(user_comments_in_news, page, per_page)

    return {
        'paginator': {
            'page': page,
            'pages': p.pages,
        },
        'objects': [
            dict(zip(['news_id', 'news_title', 'comments_amount', 'last_modified_date'], map(str, x)))
            for x in p.items
        ],
    }
