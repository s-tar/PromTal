import datetime
from PIL import Image
from application.models.file import File
from application.utils import image
from collections import defaultdict
import json
from application import Module, db
from application.models.comment import Comment
from application.utils import auth
from application.utils.validator import Validator
from flask import request
from flask.json import jsonify

module = Module('comment', __name__, url_prefix='/comment')

@module.delete("/<int:id>")
def delete(id):
    user = auth.service.get_user()
    if user.is_authorized():
        comment = Comment.get(id)
        if comment:
            comment_json = None

            def delete_parent(comment):
                should_delete = True

                if comment is not None and comment.status == Comment.Status.DELETED:
                    for quote in comment.quotes:
                        if quote.status != Comment.Status.DELETED:
                            should_delete = False
                    if should_delete:
                        db.session.delete(comment)
                        db.session.flush()
                        delete_parent(comment.quote_for)

            if comment.quotes:
                comment.status = Comment.Status.DELETED
                comment_json = get_comment_json(comment)
            else:
                db.session.delete(comment)
                db.session.flush()
                delete_parent(comment.quote_for)

            db.session.flush()
            entity = comment.get_entity()

            if entity:
                entity.after_delete_comment(comment)

            db.session.commit()
            return jsonify({'status': 'ok',
                            'comment': comment_json})

    return jsonify({'status': 'fail'})


@module.post("/new")
@module.post("/edit/<int:id>")
def save_comment(id=None):
    user = auth.service.get_user()
    data = dict(request.form)
    data['upload'] = request.files.getlist('upload')

    v = Validator(data)
    v.fields('upload').image()
    v.fields('file.id').integer(nullable=True)
    if v.is_valid():
        if not id:
            v.field('entity_name').required()
            v.field('entity_id').integer(nullable=True).required()
            if not v.valid_data.list('url') and not v.valid_data.list('upload'):
                v.field('comment').required(message="Напишите хоть что-нибудь...")
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
                    comment.modify_datetime = datetime.datetime.now()
                    comment.status = Comment.Status.MODIFIED

            if comment:
                return save(comment, data)

        v.add_error('comment', 'Что-то пошло не так... Попробуйте позже.')
    return jsonify({'status': 'fail',
                    'errors': v.errors})


@module.post("/quote/new")
@module.post("/quote/edit/<int:id>")
def save_quote(id=None):
    user = auth.service.get_user()
    data = dict(request.form)
    data['upload'] = request.files.getlist('upload')

    v = Validator(data)
    v.fields('upload').image()
    v.fields('file.id').integer(nullable=True)
    if v.is_valid():
        if not id:
            v.field('quote_for').integer().required()
            v.field('entity_name').required()
            v.field('entity_id').integer(nullable=True).required()
            if not v.valid_data.list('url') and not v.valid_data.list('upload'):
                v.field('comment').required(message="Напишите хоть что-нибудь...")

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
                    comment.modify_datetime = datetime.datetime.now()
                    comment.status = Comment.Status.MODIFIED

            if comment:
                return save(comment, data)

        v.add_error('comment', 'Что-то пошло не так... Попробуйте позже.')

    return jsonify({'status': 'fail',
                    'errors': v.errors})


def save(comment, data):
    comment.text = data.comment
    db.session.add(comment)
    db.session.flush()


    save_files(data, comment)
    entity = comment.get_entity()

    if entity:
        entity.after_add_comment(comment)

    db.session.commit()

    return jsonify({'status': 'ok',
                    'comment': get_comment_json(comment)})


def save_files(data, comment):
    ids = data.list('file.id')
    statuses = data.list('file.status')
    types = data.list('file.type')
    uploads = data.list('upload')
    urls = data.list('url')

    files = {f.id: f for f in comment.files}
    for id, status, type, url in zip(ids, statuses, types, urls):
        if id:
            file = files.get(id)
            if file and status == 'deleted':
                db.session.delete(file)
        else:
            file = File.create(name='image.png', module='comments', entity=comment, external_link=url or None)

            if file.is_local():
                file.makedir()
                img = uploads.pop(0)
                _img = Image.open(img)
                width, height = _img.size

                if width/700 < height/400:
                    image.resize(img, max_width=700).save(file.get_path())
                else:
                    image.resize(img, max_height=400).save(file.get_path())
                image.resize(img).save(file.get_path(sufix='origin'))


@module.get('/<entity>/<int:entity_id>/json/all')
def json_all_comments(entity, entity_id):
    comments = Comment.get_for(entity, entity_id, lazy=False)

    comments = {'data': [get_comment_json(comment) for comment in comments]}
    return jsonify(comments)


def get_file_json(file):
    return {
        'id': file.id,
        'type': file.name,
        'url': file.get_url(),
        'origin': file.get_url(sufix='origin')
    }


def get_comment_json(comment):
    if comment:
        author = {
            'id': comment.author.id,
            'full_name': comment.author.full_name,
            'photo': comment.author.photo.get_url() if comment.author.photo else '',
            'photo_s': comment.author.photo.get_url('thumbnail') if comment.author.photo else '',
        }
        d = comment.as_dict()
        d['status'] = Comment.Status.TITLES.get(comment.status, Comment.Status.TITLES[Comment.Status.ACTIVE])
        d['author'] = author
        d['my_vote'] = comment.my_vote.value if comment.my_vote else 0
        d['files'] = [get_file_json(f) for f in comment.files]
        if comment.status == Comment.Status.DELETED:
            d['text'] = 'Сообщение удалено'
        else:
            d['text'] = d['text'].replace('<', '&lt;').replace('>', '&gt;')
        return d

    return {}