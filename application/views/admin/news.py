from application.models.news import News
from application.views.admin.main import module
from flask import render_template, request, current_app, jsonify
from application.db import db
from application.utils.datatables_sqlalchemy.datatables import ColumnDT, DataTables
from application.models.user import User
from application.models.news import News
from application.models.news_category import NewsCategory
from application.models.news_tag import NewsTag


def _default_value(chain):
    return chain or '-'


@module.get('/news')
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


@module.get('/s_news')
def s_news():
    return render_template('admin/news/s_news.html')


@module.get('/s_news_json')
def s_news_json():
    columns = []
    columns.append(ColumnDT('id', filter=_default_value))
    columns.append(ColumnDT('title', filter=_default_value))
    query = db.session.query(News)
    rowTable = DataTables(request, News, query, columns)
    a = rowTable.output_result()
    for i in a['aaData']:
        row_id = i['0']
        last_columns = str(len(columns))
        manage_html = """Edit Delete"""
        i[last_columns] = manage_html.format()
    return jsonify(**a)