from application.models.news import News
from application.views.admin.main import admin
from flask import render_template, request, current_app, jsonify, url_for
from application.db import db
from application.utils.datatables_sqlalchemy.datatables import ColumnDT, DataTables
from application.models.user import User
from application.models.news import News
from application.models.news_category import NewsCategory
from application.models.news_tag import NewsTag
from application.models.view_news import ViewNews
from application.utils.datatables_sqlalchemy.datatables import row2dict


def _default_value(chain):
    return chain or '-'


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


@admin.get('/s_news')
def s_news():
    return render_template('admin/news/s_news.html')


@admin.get('/s_news_json')
def s_news_json():
    columns = []
    columns.append(ColumnDT('news_id', filter=_default_value))
    columns.append(ColumnDT('news_title', filter=_default_value))# 1
    columns.append(ColumnDT('user_full_name', filter=_default_value))# 2
    columns.append(ColumnDT('news_category_name', filter=_default_value))# 3
    #
    columns.append(ColumnDT('users_id', filter=_default_value))# 4
    columns.append(ColumnDT('news_category_id', filter=_default_value))# 5
    query = db.session.query(ViewNews)
    rowTable = DataTables(request, ViewNews, query, columns)
    a = rowTable.output_result()
    for i in a['aaData']:
        row_id = i['0']
        i['1'] = "<a href='"+url_for('news.news_one', id=row_id)+"'>"+i['1']+"</a>"
        i['2'] = "<a href='"+url_for('user.profile_id', user_id=i['4'])+"'>"+i['2']+"</a>"
        i['3'] = "<a href='"+i['5']+"'>"+i['3']+"</a>"
        last_columns = str(4)
        manage_html = """Edit Delete"""
        i[last_columns] = manage_html.format()
    return jsonify(**a)