from application import Module
from application.models.news import News
from application.views.main import main
from flask import render_template

module = Module('news', __name__, url_prefix='/news')

@main.get("/")
@module.get('/')
def list_all():
    news = News.all()
    return render_template('news/all.html', **{'news': news})