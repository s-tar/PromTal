from application.models.news import News
from application.views.admin.main import admin
from flask import render_template, request, current_app


@admin.get('/news')
def news_index():
    news = News.query.order_by(News.datetime.asc())
    page = request.args.get('page', 1, type=int)
    pagination = news.paginate(
        page,
        per_page=current_app.config['ADMIN_NEWS_PER_PAGE'],
        error_out=False
    )
    news = pagination.items
    return render_template(
        'admin/news/index.html',
        news=news,
        pagination=pagination
    )