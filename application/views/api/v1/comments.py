from flask import request, current_app

from . import api_v1

from application.db import db
from application.models.comment import Comment
from application.models.serializers.comment import comment_schema
from application.views.api.decorators import json


@api_v1.get('/comments')
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
        'objects': [x.to_json().data for x in p.items]
    }


@api_v1.get('/comment/<int:id>')
@json()
def get_comment_item(id):
    comment = Comment.query.get_or_404(id)
    return comment.to_json().data


@api_v1.delete('/comment/<int:id>')
@json()
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    return {}, 204


@api_v1.put('/comment/<int:id>')
@json()
def edit_comment(id):
    comment = Comment.query.get_or_404(id)

    for field, value in comment_schema.load(request.get_json()).data.items():
        setattr(comment, field, value)

    db.session.commit()
    return {}, 200


@api_v1.post('/comments')
@json()
def create_comment():
    comment = Comment()

    print(comment)
    for field, value in comment_schema.load(request.get_json()).data.items():
        setattr(comment, field, value)

    db.session.add(comment)
    db.session.commit()
    return comment.to_json().data, 200
