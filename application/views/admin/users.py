from flask import render_template

from application.views.admin.main import admin
from application.models.user import User


@admin.get('/users')
def users_index():
    users = User.query.order_by(User.full_name.desc()).all()
    return render_template('admin/users/index.html', users=users)