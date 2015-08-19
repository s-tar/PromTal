from application.models.community import Community
from application.models.file import File
from collections import defaultdict
from application import Module, db
from application.models.news import News
from application.utils import auth
from application.utils.validator import Validator
from flask import render_template, request, abort, redirect, url_for
from flask.json import jsonify
from application.views.main import main
from application import utils

module = Module('community', __name__, url_prefix='/community')

@module.before_request
def before_request():
    user = auth.service.get_user()
    if not user.is_authorized():
        return redirect(url_for('login.login'))


@main.get('/communities')
def list_communities():
    communities = Community.all()
    return render_template('community/all.html', **{'communities': communities})


@module.get('/<int:id>')
def community_page(id):
    community = Community.get(id)
    return render_template('community/one.html', **{'community': community})

@module.get('/new')
@module.get('/edit/<int:id>')
def news_form(id=None):
    community = Community.get(id) or Community()
    categories = defaultdict(list)
    if id and community.owner != auth.service.get_user():
        abort(403)
    return render_template('community/form.html', **{'community': community})

@module.route("/save", methods=['POST'])
def save():
    data = dict(request.form)
    data['image'] = request.files.getlist('image')
    v = Validator(data)
    v.fields('id').integer(nullable=True)
    v.field('name').required()
    v.field('private').boolean()
    v.field('description').required()
    v.field('image').image()
    user = auth.service.get_user()
    if not user.is_authorized():
        abort(403)
    if v.is_valid():
        data = v.valid_data
        community = Community()
        if data.id:
            community = Community.get(data.id)
        if not community or (community.owner and community.owner != user):
            abort(403)
        community.type = Community.TYPE.PRIVATE if data.private else Community.TYPE.PUBLIC
        community.name = data.name
        community.description = data.description
        community.owner = user

        db.session.add(community)
        db.session.flush()
        image = data.image
        if image:
            img = community.image = community.image or File.create(name='image.png', module='community', entity=community)
            img.makedir()
            img.update_hash()
            utils.image.thumbnail(image, width=200, height=200, fill=utils.image.COVER).save(img.get_path())
        db.session.commit()
        return jsonify({'status': 'ok',
                        'community': community.as_dict()})

    return jsonify({'status': 'fail',
                    'errors': v.errors})


@module.delete("/<int:id>")
def delete(id):
    user = auth.service.get_user()
    if user.is_authorized():
        news = News.get(id)
        if news:
            db.session.delete(news)
            db.session.commit()
            return jsonify({'status': 'ok'})

    return jsonify({'status': 'fail'})