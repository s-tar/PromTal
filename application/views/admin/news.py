from application.views.admin.main import admin
from flask import render_template


@admin.get('/news')
def news_index():
    return render_template('admin/news/index.html')