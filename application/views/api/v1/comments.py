from flask import request, current_app

from . import api_v1

from application.models.comment import Comment
from application.views.api.decorators import json


@api_v1.get('/comments/')
@json()
def get_comments():

    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', current_app.config['ADMIN_COMMENTS_PER_PAGE'],
                                    type=int), current_app.config['ADMIN_COMMENTS_PER_PAGE'])

    comments = (
        Comment.query
        .order_by(Comment.datetime.desc())
    )
    p = comments.paginate(page, per_page)

    return {
        'paginator': {
            'page': page,
            'pages': p.pages,
        },
        'objects': [x.to_json() for x in p.items]
    }
