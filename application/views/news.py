from collections import defaultdict

from flask import render_template, request, abort, redirect, url_for
from flask.json import jsonify

from application import Module, db
from application.utils.decorators import requires_permissions
from application.utils import auth
from application.utils.validator import Validator
from application.models.user import User
from application.models.news import News
from application.models.news_category import NewsCategory
from application.models.news_tag import NewsTag
from application.views.main import main
from application.tasks.email import send_news_notification

module = Module('news', __name__, url_prefix='/news')

@module.before_request
def before_request():
    user = auth.service.get_user()
    if not user.is_authorized():
        return redirect(url_for('login.login'))


@main.get("/")
@module.get('/')
def list_all():
    news = News.all()
    return render_template('news/all.html', **{'news': news})

@module.get('/category/<int:id>')
def list_all_by_category(id):
    category = NewsCategory.get(id)
    return render_template('news/all.html', **{'category': category, 'news': category.news})

@module.get('/tag/<int:id>')
def list_all_by_tag(id):
    tag = NewsTag.get(id)
    news = News.all_by_tag(tag) if tag else []
    return render_template('news/all.html', **{'tag': tag, 'news': news})

@module.get('/<int:id>')
def news_one(id):
    news = News.query.get_or_404(id)
    news.increment_views()
    return render_template('news/one.html', **{'news': news})

@module.get('/new')
@module.get('/edit/<int:id>')
@requires_permissions('write_articles')
def news_form(id=None):
    news = News.get(id) or News()
    categories = defaultdict(list)
    for c in NewsCategory.all():
        categories[c.parent_id].append(c)
    return render_template('news/form.html', **{'news': news, 'categories': categories})

@module.route("/save", methods=['POST'])
def save():
    v = Validator(request.form)
    v.fields('id').integer(nullable=True)
    v.field('title').required()
    v.field('text').required()
    v.field('category_id').integer(nullable=True)
    user = auth.service.get_user()
    if not user.is_authorized():
        abort(403)
    if v.is_valid():
        data = v.valid_data

        news = News.get(data.id)

        if news:
            news.title = data.title
            news.text = data.text
        else:
            news = News()
            news.title = data.title
            news.text = data.text
            news.author = user

        category = NewsCategory.get(data.category_id)
        news.category = category

        tags = data.list('tag')
        existing_tags = {tag.name: tag for tag in NewsTag.get_tags(tags)}
        tags = {tag: NewsTag(name=tag) for tag in tags}
        tags.update(existing_tags)

        news.tags = list(tags.values())

        is_new = True if user.id is not None else False
        db.session.add(news)
        db.session.commit()

        if is_new:
            send_news_notification.delay(news.id, news.title)

        return jsonify({'status': 'ok',
                        'news': news.as_dict()})

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