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


@module.post("/new")
@module.post("/edit/<int:id>")
def save_comment(id=None):
    user = auth.service.get_user()
    data = dict(request.form)
    data['upload'] = request.files.getlist('upload')
    v = Validator(data)
    v.fields('upload').image()
    if v.is_valid():
        if not id:
            v.field('entity_name').required()
            v.field('entity_id').integer(nullable=True).required()
            if v.valid_data.list('entity_id') == 0:
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

    if v.is_valid():
        if not id:
            v.field('quote_for').integer().required()
            v.field('entity_name').required()
            v.field('entity_id').integer(nullable=True).required()
            if v.valid_data.list('entity_id') == 0:
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
                return save(comment, data)


        v.add_error('comment', 'Что-то пошло не так... Попробуйте позже.')

    return jsonify({'status': 'fail',
                    'errors': v.errors})


def save(comment, data):
    comment.text = data.comment

    db.session.add(comment)
    db.session.flush()

    save_files(data.list("url"), data.list("upload"), data.list('file.type'), comment)
    entity = comment.get_entity()

    if entity:
        entity.after_add_comment(comment)

    db.session.commit()

    files = [get_file_json(f) for f in comment.files]
    return jsonify({'status': 'ok',
                    'comment': get_comment_json(comment, files)})


def save_files(urls, uploads, types, comment):
    for url, type in zip(urls, types):
        file = File.create(name='image.png', module='comments', entity=comment, external_link=url or None)

        if file.is_local():
            file.makedir()
            img = uploads.pop(0)
            image.thumbnail(img, width=450, height=300, fill=image.COVER).save(file.get_path())
            image.resize(img).save(file.get_path(sufix='origin'))


@module.get('/<entity>/<int:entity_id>/json/all')
def json_all_comments(entity, entity_id):
    comments = Comment.get_for(entity, entity_id, lazy=False)
    files = defaultdict(list)
    for f in File.get(module='comments', entity=comments):
        files[f.entity].append(get_file_json(f))
    comments = {'data': [get_comment_json(comment, files.get(File.stringify_entity(comment), [])) for comment in comments] }
    return jsonify(comments)


def get_file_json(file):
    return {
        'url': file.get_url(),
        'origin': file.get_url(sufix='origin')
    }


def get_comment_json(comment, files=[]):
    if comment:
        author = {
            'id': comment.author.id,
            'full_name': comment.author.full_name,
            'photo': comment.author.photo.get_url() if comment.author.photo else '',
            'photo_s': comment.author.photo.get_url('thumbnail') if comment.author.photo else '',
        }
        d = comment.as_dict()
        d['author'] = author
        d['files'] = files
        d['text'] = d['text'].replace('<', '&lt;').replace('>', '&gt;')
        return d

    return {}