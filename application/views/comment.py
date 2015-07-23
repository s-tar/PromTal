from application import Module, db
from application.models.comment import Comment
from application.utils import auth
from application.utils.validator import Validator
from flask import request
from flask.json import jsonify

module = Module('comment', __name__, url_prefix='/comment')


@module.post("/new")
def new_comment():
    v = Validator(request.form)
    v.field('entity_id').integer(nullable=True)
    v.field('comment').required()
    if v.is_valid():
        if save_comment(v.valid_data):
            return jsonify({'status': 'ok'})

    v.add_error('comment', 'Что-то пошло не так... Попробуйте позже.')
    return jsonify({'status': 'fail',
                    'errors': v.errors})


@module.post("/quote/new")
def new_quote():
    v = Validator(request.form)
    v.field('quote_for').integer()
    v.field('comment').required()
    if v.is_valid():
        if save_comment(v.valid_data):
            return jsonify({'status': 'ok'})

    v.add_error('comment', 'Что-то пошло не так... Попробуйте позже.')
    return jsonify({'status': 'fail',
                    'errors': v.errors})


@module.post("/edit")
def edit_comment():
    v = Validator(request.form)
    v.field('id').integer()
    v.field('comment').required()
    if v.is_valid():
        if save_comment(v.valid_data):
            return jsonify({'status': 'ok'})

    v.add_error('comment', 'Что-то пошло не так... Попробуйте позже.')
    return jsonify({'status': 'fail',
                    'errors': v.errors})


def save_comment(data):
    user = auth.service.get_user()
    id = data.id or None
    entity = data.entity_name or None
    entity_id = data.entity_id or None
    quote_for = data.quote_for or None
    if user.is_authorized() and (id or quote_for or (entity and entity_id)):
        if not id:
            comment = Comment()
            comment.entity = entity
            comment.entity_id = entity_id
            comment.quote_for_id = quote_for
            comment.author_id = user.id
        else:
            comment = Comment.get(id)
            if not comment:
                return False

        comment.text = data.comment

        db.session.add(comment)
        db.session.commit()
        return True
    return False