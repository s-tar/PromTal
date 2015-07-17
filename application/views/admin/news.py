from application.views.admin.main import admin
from flask import render_template


@admin.get('/news')
def new_admin():
    return render_template('news/index.html')