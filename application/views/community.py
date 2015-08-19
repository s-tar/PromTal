from application.models.community import Community
from application.models.file import File
from application import Module, db
from application.models.post import Post
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
def community_form(id=None):
    community = Community.get(id) or Community()
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
    if not v.is_valid():
        return jsonify({
            'status': 'fail',
            'errors': v.errors
        })

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


@module.delete("/<int:id>")
def delete(id):
    user = auth.service.get_user()
    if user.is_authorized():
        community = Community.get(id)
        if community:
            db.session.delete(community)
            db.session.commit()
            return jsonify({'status': 'ok'})

    return jsonify({'status': 'fail'})


@module.get('/<int:community_id>/post/<int:id>')
def post_page(community_id, id):
    post = Post.get(id)
    return render_template('community/post_one.html', **{'post': post})


@module.get('/<int:community_id>/post/new')
@module.get('/<int:community_id>/post/edit/<int:id>')
def post_form(community_id, id=None):
    user = auth.service.get_user()
    community = Community.get(community_id)
    post = Post.get(id) if id else Post()

    if not community or not post:
        abort(404)

    if not community.is_member(user) or (id and post.author != user):
        abort(403)

    return render_template('community/post_form.html', **{'community_id': community_id, 'post': post})


@module.route("/post/save", methods=['POST'])
def post_save():
    v = Validator(request.form)
    v.fields('id').integer(nullable=True)
    v.field('title').required()
    v.field('text').required()
    v.field('community_id').required().integer()
    user = auth.service.get_user()

    if not user.is_authorized():
        abort(403)

    if not v.is_valid():
        return jsonify({
            'status': 'fail',
            'errors': v.errors
        })

    data = v.valid_data
    if not data.id:
        post = Post()
        post.community_id = data.community_id
    else:
        post = Post.get(data.id)

    if not post:
        abort(400)
    if post.author and post.author != user:
        abort(403)
    post.title = data.title
    post.text = data.text
    post.author = user

    db.session.add(post)
    db.session.commit()

    return jsonify({
        'status': 'ok',
        'post': post.as_dict()
    })