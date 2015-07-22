from application import Module, db
from application.models.news import News
from application.utils import auth
from application.utils.validator import Validator
from application.views.main import main
from flask import render_template, request
from flask.json import jsonify

module = Module('news', __name__, url_prefix='/news')

@main.get("/")
@module.get('/')
def list_all():
    news = News.all()
    return render_template('news/all.html', **{'news': news})


@module.get('/<int:id>')
def news_one(id):
    news = News.get(id)
    return render_template('news/one.html', **{'news': news})

@module.get('/new')
@module.get('/edit/<int:id>')
def news_form(id=None):
    news = News.get(id) or News()
    return render_template('news/form.html', **{'news': news})

@module.route("/save", methods=['POST'])
def save():
    v = Validator(request.form)
    v.fields('id').integer(nullable=True)
    v.field('title').required()
    v.field('text').required()
    user = auth.service.get_user()
    if not user.is_authorized():
        v.add_error('title', 'Сорян, паца. Нет пользователя - нет новости.')
    if v.is_valid():
        data = v.valid_data
        news = News.get(data.id) or News()
        news.title = data.title
        news.text = data.text
        news.author = user
        db.session.add(news)
        db.session.commit()
        return jsonify({'status': 'ok',
                        'news': news.as_dict()})

    return jsonify({'status': 'fail',
                    'errors': v.errors})