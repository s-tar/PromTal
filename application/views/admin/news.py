from application.models.news import News
from application.views.admin.main import admin
from flask import render_template


@admin.get('/news')
def news_index():
    news = News.query.order_by(News.datetime.asc())
    return render_template('admin/news/index.html', news=news)