from flask import render_template, request, url_for, redirect, jsonify
from application.views.admin.main import module
from application.models.view_news_category import ViewNewsCategory
from application import db
from application.utils.datatables_sqlalchemy.datatables import ColumnDT, DataTables


def _default_value(chain):
    return chain or '-'

def _default_int(chain):
    return '0' if chain == "None" else chain


@module.get('/news_categories')
def news_categories():
    return render_template('admin/news_category/categories.html')


@module.get('/news_categories_json')
def news_categories_json():
    columns = []
    columns.append(ColumnDT('news_category_id', filter=_default_value))
    columns.append(ColumnDT('news_category_name', filter=_default_value))
    columns.append(ColumnDT('count_news', filter=_default_int))
    columns.append(ColumnDT('count_views', filter=_default_int))
    columns.append(ColumnDT('count_votes', filter=_default_int))
    columns.append(ColumnDT('count_comments', filter=_default_int))
    query = db.session.query(ViewNewsCategory)
    rowTable = DataTables(request, ViewNewsCategory, query, columns)
    a = rowTable.output_result()
    for row in a['aaData']:
        row_id = row['0']
        row['1'] = "<a href='"+url_for('news.list_all_by_category', id=row_id)+"'>"+row['1']+"</a>"
        last_columns = str(len(columns))
        manage_html = """
            <a href="{edit_user_profile}">
                <span class="glyphicon glyphicon-pencil" aria-hidden="true"></span>
            </a>
            <a href="{delete_user_profile}">
                <span class="glyphicon glyphicon-trash" aria-hidden="true"></span>
            </a>
        """
        row[last_columns] = manage_html.format(
            edit_user_profile = url_for('admin.edit_user', id=row_id),
            delete_user_profile = url_for('admin.delete_user', id=row_id))
    return jsonify(**a)

