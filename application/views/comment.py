from collections import defaultdict
import json
from application import Module, db
from application.models.comment import Comment
from application.utils import auth
from application.utils.validator import Validator
from flask import request
from flask.json import jsonify

module = Module('comment', __name__, url_prefix='/comment')


@module.post("/new")
@module.post("/edit/<int:id>")
def new_comment(id=None):
    user = auth.service.get_user()
    v = Validator(request.form)
    v.field('comment').required()
    if v.is_valid():
        if not id:
            v.field('entity_name').required()
            v.field('entity_id').integer(nullable=True).required()
        if v.is_valid() and user.is_authorized():
            data = v.valid_data
            if not id:
                comment = Comment()
                comment.author_id = user.id
                comment.entity = data.entity_name
                comment.entity_id = data.entity_id
            else:
                comment = Comment.get(id)

            if comment:
                comment.text = data.comment

                db.session.add(comment)
                db.session.commit()

                entity = comment.get_entity()
                if entity:
                    entity.after_add_comment(comment)
                return jsonify({'status': 'ok',
                                'comment': get_comment_json(comment)})

        v.add_error('comment', 'Что-то пошло не так... Попробуйте позже.')
    return jsonify({'status': 'fail',
                    'errors': v.errors})


@module.post("/quote/new")
@module.post("/quote/edit/<int:id>")
def save_quote(id=None):
    user = auth.service.get_user()
    v = Validator(request.form)
    v.field('comment').required()
    if v.is_valid():
        if not id:
            v.field('quote_for').integer().required()

        if v.is_valid() and user.is_authorized():
            data = v.valid_data
            comment = None
            if not id:
                quote_for = Comment.get(v.valid_data.quote_for)
                if quote_for:
                    comment = Comment()
                    comment.author_id = user.id
                    comment.quote_for = quote_for
                    comment.entity = quote_for.entity
                    comment.entity_id = quote_for.entity_id
            else:
                comment = Comment.get(id)

            if comment:
                comment.text = data.comment

                db.session.add(comment)
                db.session.commit()

                entity = comment.get_entity()
                if entity:
                    entity.after_add_comment(comment)
                return jsonify({'status': 'ok',
                                'comment': get_comment_json(comment)})

        v.add_error('comment', 'Что-то пошло не так... Попробуйте позже.')

    return jsonify({'status': 'fail',
                    'errors': v.errors})

@module.get('/<entity>/<int:entity_id>/json/all')
def json_all_comments(entity, entity_id):
    comments = Comment.get_for(entity, entity_id, lazy=False)
    comments = {'data': [get_comment_json(comment) for comment in comments] }
    return jsonify(comments)


def get_comment_json(comment):
    if comment:
        author = {
            'id': comment.author.id,
            'full_name': comment.author.full_name,
            'photo': comment.author.photo,
            'photo_s': comment.author.photo_s,
        }
        d = comment.as_dict()
        d['author'] = author
        return d

    return {}