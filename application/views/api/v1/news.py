from flask import request, current_app

from . import api_v1

from application import db
from application.models.news import News
from application.models.serializers.news import news_schema
from application.views.api.decorators import json


@api_v1.get('/news/')
@json()
def get_news():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', current_app.config['ADMIN_NEWS_PER_PAGE'],
                                    type=int), current_app.config['ADMIN_NEWS_PER_PAGE'])

    news = (
        News.query
        .order_by(News.datetime.desc())
    )
    p = news.paginate(page, per_page)
    print(p.items[0])
    return {
        'paginator': {
            'page': page,
            'pages': p.pages,
        },
        'objects': [x.to_json().data for x in p.items],
    }


@api_v1.get('/news/<int:id>/')
@json()
def get_news_item(id):
    news = News.query.get_or_404(id)
    return news.to_json().data


@api_v1.delete('/news/<int:id>/')
@json()
def delete_news(id):
    news = News.query.get_or_404(id)
    db.session.delete(news)
    db.session.commit()
    return {}, 204


@api_v1.put('/news/<int:id>/')
@json()
def edit_news(id):
    news = News.query.get_or_404(id)

    result = news_schema.load(request.get_json())

    if result.errors:
        return result.errors, 400

    for field, value in result.data.items():
        setattr(news, field, value)

    db.session.commit()
    return news.to_json().data, 200


@api_v1.post('/news/')
@json()
def create_news():
    result = news_schema.load(request.get_json())

    if result.errors:
        return result.errors, 400

    news = News(**result.data)

    db.session.add(news)
    db.session.commit()
    return news.to_json().data, 200
