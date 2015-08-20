from flask import render_template, request, current_app, jsonify, url_for
from werkzeug.utils import redirect

from application.db import db
from application.utils.datatables_sqlalchemy.datatables import ColumnDT, DataTables
from application.models.news import News
from application.models.view_news import ViewNews
from application.views.admin.main import module


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
    columns = list()
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
        i['1'] = "<a href='"+url_for('news.news_one', id=int(row_id))+"'>"+i['1']+"</a>"
        i['2'] = "<a href='"+url_for('user.profile', user_id=int(i['4']))+"'>"+i['2']+"</a>"
        if i['5'] == 'None':
            i['3'] = "-"
        else:
            i['3'] = "<a href='"+url_for('news.list_all_by_category', id=i['5'])+"'>"+i['3']+"</a>"
        last_columns = str(4)
        last_columns = str(len(columns))
        manage_html = """Edit Delete"""
        i[last_columns] = manage_html.format()
    return jsonify(**a)


@module.get('/news/delete/<int:id>')
def delete_news(id):
    news = News.query.get_or_404(id)
    news.status = News.STATUS_DELETED
    db.session.commit()
    return redirect(url_for('admin.news_index'))


@module.get('/news/activate/<int:id>')
def activate_news(id):
    news = News.query.get_or_404(id)
    news.status = News.STATUS_ACTIVE
    db.session.commit()
    return redirect(url_for('admin.news_index'))


@module.get('/news/block/<int:id>')
def block_news(id):
    news = News.query.get_or_404(id)
    news.status = News.STATUS_BLOCKED
    db.session.commit()
    return redirect(url_for('admin.news_index'))