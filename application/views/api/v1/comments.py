from flask import request, current_app

from . import api_v1

from application.db import db
from application.models.comment import Comment
from application.models.serializers.comment import comment_schema
from application.views.api.decorators import json


@api_v1.get('/comments/')
@json()
def get_comments():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', current_app.config['ADMIN_COMMENTS_PER_PAGE'],
                                    type=int), current_app.config['ADMIN_COMMENTS_PER_PAGE'])

    comments = (
        Comment.query
        .order_by(Comment.id.desc())
    )
    p = comments.paginate(page, per_page)

    return {
        'paginator': {
            'page': page,
            'pages': p.pages,
        },
        'objects': [x.to_json().data for x in p.items],
    }


@api_v1.get('/comments/<int:id>/')
@json()
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    return comment.to_json().data


@api_v1.delete('/comments/<int:id>/')
@json()
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    return {}, 204


@api_v1.put('/comments/<int:id>/')
@json()
def edit_comment(id):
    comment = Comment.query.get_or_404(id)

    result = comment_schema.load(request.get_json())

    if result.errors:
        return result.errors, 400

    for field, value in result.data.items():
        setattr(comment, field, value)

    db.session.commit()
    return comment.to_json().data, 200


@api_v1.post('/comments/')
@json()
def create_comment():
    result = comment_schema.load(request.get_json())

    if result.errors:
        return result.errors, 400

    comment = Comment(**result.data)

    db.session.add(comment)
    db.session.commit()
    return comment.to_json().data, 200
