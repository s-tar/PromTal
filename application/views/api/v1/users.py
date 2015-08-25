from application.models.file import File
from application.utils import image
from flask import request, current_app, abort
from flask.ext.sqlalchemy import BaseQuery
from sqlalchemy import func, desc

from . import api_v1

from application.db import db
from application.models.user import User
from application.models.news import News
from application.models.comment import Comment
from application.models.serializers.user import user_schema
from application.utils.validator import Validator
from application.utils import auth
from application.bl.users import create_user, update_user, DataProcessingError
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
@json()
def add_user():
    v = Validator(request.form)
    v.field('name').required()
    v.field('surname').required()
    v.field('file').image()
    v.field('email').required().email()
    v.field('login').required()
    v.field('department').required()
    v.field('groups').required()
    v.field('mobile_phone').required().phone_number()
    v.field('birth_date').datetime(format='%d.%m.%Y')
    if v.is_valid():
        data = {
            'name': v.valid_data.name,
            'surname': v.valid_data.surname,
            'email': v.valid_data.email,
            'login': v.valid_data.login,
            'department': v.valid_data.department,
            'groups': v.valid_data.list('groups'),
            'mobile_phone': v.valid_data.mobile_phone,
            'skype': v.valid_data.skype,
            'birth_date': v.valid_data.birth_date,
            'photo': v.valid_data.file
        }

        already_used_login = User.get_by_login(data['login'])
        already_used_email = User.get_by_email(data['email'])

        if already_used_login:
            v.add_error('login', 'Такой логин уже занят')
        if already_used_email:
            v.add_error('email', 'Такой email уже занят')

        if already_used_login or already_used_email:
            return {"status": "fail", "errors": v.errors}

        try:
            create_user(**data)
            if data['photo']:
                p = File.create(name='photo.png', module='users', entity=User.get_by_login(data['login']))
                p.makedir()
                p.update_hash()
                image.thumbnail(data["photo"], width=100, height=100, fill=image.COVER).save(p.get_path(sufix="thumbnail"))
                image.resize(data["photo"]).save(p.get_path())

            return {"status": "ok"}
        except DataProcessingError as e:
            return {'status': 'failOnProcess', 'error': e.value}

    return {"status": "fail", "errors": v.errors}


@api_v1.put('/users/<int:id>/')
@json()
def edit_user(id):
    #  --- HARDCODE ZONE begin ---
    current_user = auth.service.get_user()
    if not current_user.has_permission('manage_users') and current_user.id != id:
        abort(403)
    #  --- HARDCODE ZONE end ---

    v = Validator(request.form)
    v.field('name').required()
    v.field('surname').required()
    v.field('file').image()
    v.field('email').required().email()
    v.field('login').required()
    v.field('department').required()
    v.field('mobile_phone').required().phone_number()
    v.field('birth_date').datetime(format='%d.%m.%Y')
    if v.is_valid():
        edited_user = User.get_by_id(id)
        duplicate_error = False
        data = {
            'id': id,
            'full_name': "{0} {1}".format(v.valid_data.name, v.valid_data.surname),
            'email': v.valid_data.email,
            'login': v.valid_data.login,
            'department': v.valid_data.department,
            'mobile_phone': v.valid_data.mobile_phone,
            'inner_phone': v.valid_data.inner_phone,
            'position': v.valid_data.position,
            'skype': v.valid_data.skype,
            'birth_date': v.valid_data.birth_date,
            'photo': v.valid_data.file
        }

        user_with_same_login = User.get_by_login(data['login'])
        user_with_same_email = User.get_by_email(data['email'])

        if user_with_same_login and user_with_same_login != edited_user:
            duplicate_error = True
            v.add_error('login', 'Такой логин уже занят')
        if user_with_same_email and user_with_same_email != edited_user:
            duplicate_error = True
            v.add_error('email', 'Такой email уже занят')

        if duplicate_error:
            return {"status": "fail", "errors": v.errors}

        try:
            update_user(**data)
            if data['photo']:
                p = File.create(name='photo.png', module='users', entity=User.get_by_login(data['login']))
                p.makedir()
                p.update_hash()
                image.thumbnail(data["photo"], width=100, height=100, fill=image.COVER).save(p.get_path(sufix="thumbnail"))
                image.resize(data["photo"]).save(p.get_path())

            return {"status": "ok"}
        except DataProcessingError as e:
            return {'status': 'failOnProcess', 'error': e.value}

    return {"status": "fail", "errors": v.errors}


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
