from flask import request
from flask.json import jsonify

from application import Module, db
from application.utils import auth
from application.utils.validator import Validator
from application.models.vote import Vote

module = Module('vote', __name__, url_prefix='/vote')


@module.delete("/<int:id>")
def delete(id):
    user = auth.service.get_user()
    if user.is_authorized():
        vote = Vote.get(id)
        if vote and vote.user == user:
            db.session.delete(vote)
            db.session.flush()
            entity = vote.get_entity()

            if entity:
                entity.after_delete_vote(vote)

            db.session.commit()
            return jsonify({'status': 'ok',
                            'vote': vote.as_dict()})

    return jsonify({'status': 'fail'})


@module.post("/like")
def like_route():
    user = auth.service.get_user()
    v = Validator(request.form)
    v.field('value').boolean().required()
    v.field('entity').required()
    v.field('entity_id').integer().required()
    if user.is_authorized() and v.is_valid():
        data = v.valid_data
        vote = Vote.get_for(data.entity, data.entity_id, user) or Vote()
        vote.user = user
        vote.entity = data.entity
        vote.entity_id = data.entity_id
        vote.value = 0 if vote.value else 1
        vote.type = Vote.Type.LIKE
        db.session.add(vote)

        delta = 1 if vote.value else -1 if vote.id else 0
        entity = vote.get_entity()
        if entity:
            entity.after_update_vote(delta)

        db.session.commit()
        return jsonify({'status': 'ok',
                        'vote': vote.as_dict(),
                        'count': entity.votes_count if entity else 0})

    return jsonify({'status': 'fail'})


# @module.post("/vote/<int:value>")
# def vote(value, type):
#     user = auth.service.get_user()
#     v = Validator(request.form)
#     v.field('entity').required()
#
#     if user.is_authorized() and v.is_valid():
#         data = v.valid_data
#         vote = Vote.get_for(entity=data.entity, user=user) or Vote()
#         vote.user = user
#         vote.entity = data.entity
#         vote.value = value
#         vote.type = type
#         db.session.add()
#
#         entity = vote.get_entity()
#
#         if entity:
#             entity.after_add_vote(vote)
#
#         db.session.commit()
#         return jsonify({'status': 'ok',
#                         'vote': vote.as_dict()})
#
#     return jsonify({'status': 'fail'})