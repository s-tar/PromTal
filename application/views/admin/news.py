from application.views.admin.main import module
from flask import render_template


@module.get('/news')
def new_admin():
    return render_template('news/index.html')