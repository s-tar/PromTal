from application import db
from flask import request, current_app

from . import api_v1

from application.models.news import News
from application.views.api.decorators import json


@api_v1.get('/news/')
@json()
def get_news():

    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', current_app.config['ADMIN_NEWS_PER_PAGE'],
                                    type=int), current_app.config['ADMIN_NEWS_PER_PAGE'])

    posts = (
        News.query
        .order_by(News.datetime.desc())
    )
    p = posts.paginate(page, per_page)

    return {
        'paginator': {
            'page': page,
            'pages': p.pages,
        },
        'objects': [x.to_json() for x in p.items]
    }


@api_v1.get('/news/<int:id>')
@json()
def _get_news(id):
    post = (
        News.query.get_or_404(id)
    )
    return post.to_json()


@api_v1.delete('/news/<int:id>')
@json()
def delete_news(id):
    post = (
        News.query.get(id)
    )
    db.session.delete(post)
    db.session.commit()
    return {}, 204


@api_v1.put('/news/<int:id>')
@json()
def edit_news(id):
    name = request.form.get('name')
    email = request.form.get('email')
    full_name = request.form.get('full_name')
    post = (
        News.query.get(id)
    )
    post.name = name
    post.email = email
    post.full_name = full_name

    db.session.add(post)
    db.session.commit()
    return {}, 200


@api_v1.post('/news/')
@json()
def create_news():
    login = request.form.get()
    email = request.form.get('email')
    full_name = request.form.get('full_name')
    post = News()
    post.full_name = full_name
    post.email = email
    post.login = login
    db.session.add(post)
    db.session.commit()
    return post.to_json(), 200
