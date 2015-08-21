from application.models.community import Community, CommunityMember
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
    communities = Community.all_active()
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
        if community and community.owner == user:
            community.status = community.STATUS.DELETED
            db.session.commit()
            return jsonify({'status': 'ok'})

    return jsonify({'status': 'fail'})


@module.get('/<int:community_id>/post/<int:id>')
def post_page(community_id, id):
    post = Post.get(id)
    post.increment_views()
    return render_template('community/post_one.html', **{'post': post})


@module.get('/<int:community_id>/post/new')
@module.get('/<int:community_id>/post/edit/<int:id>')
def post_form(community_id, id=None):
    user = auth.service.get_user()
    community = Community.get(community_id)
    post = Post.get(id) if id else Post()

    if not community or not post:
        abort(404)

    if not community.has_member(user) or (id and post.author != user):
        abort(403)

    return render_template('community/post_form.html', **{'community': community, 'post': post})


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

@module.delete("/post/<int:id>")
def post_delete(id):
    user = auth.service.get_user()
    if user.is_authorized():
        post = Post.get(id)
        if post and post.author == user:
            db.session.delete(post)
            db.session.commit()
            return jsonify({'status': 'ok', 'community': post.community.as_dict()})

    return jsonify({'status': 'fail'})


@module.route("/subscription/<int:community_id>", methods=['POST'])
def subscribe(community_id):
    subscription = True if request.form['subscription'] == 'subscribe' \
        else False if request.form['subscription'] == 'unsubscribe' \
        else None
    user = utils.auth.service.get_user()
    if not user.is_authorized:
        abort(403)

    community = Community.get(community_id)
    if not community:
        abort(404)

    if community.owner != user:
        if subscription is True and not community.has_member(user):
            cm = CommunityMember(user=user, community=community)
            if community.type == community.TYPE.PUBLIC:
                cm.status = cm.STATUS.ACCEPTED
            db.session.add(cm)
            db.session.commit()
        elif subscription is False and community.has_member(user):
            community.members.remove(user)
            db.session.commit()

    res = {
        'status': 'ok',
        'community': community.as_dict(),
        'subscribed': community.has_member(user)
    }
    res['community']['type'] = community.TYPE.TITLE[community.type]
    res['community']['count_members'] = community.count_members

    return jsonify(res)