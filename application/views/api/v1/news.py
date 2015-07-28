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

    news = (
        News.query
        .order_by(News.datetime.desc())
    )
    p = news.paginate(page, per_page)

    return {
        'paginator': {
            'page': page,
            'pages': p.pages,
        },
        'objects': [x.to_json() for x in p.items]
    }