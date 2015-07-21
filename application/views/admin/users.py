from flask import render_template, request, current_app

from application.views.admin.main import admin
from application.models.user import User


@admin.get('/users')
def users_index():
    users = User.query.order_by(User.full_name.asc())
    page = request.args.get('page', 1, type=int)
    pagination = users.paginate(
        page,
        per_page=current_app.config['ADMIN_USERS_PER_PAGE'],
        error_out=False
    )
    users = pagination.items
    return render_template('admin/users/index.html', users=users,
                           pagination=pagination)