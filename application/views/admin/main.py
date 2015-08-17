from flask import render_template, redirect, url_for

from application import Module
from application.utils import auth

module = Module('admin', __name__, url_prefix='/admin')


@module.before_request
def before_request():
    user = auth.service.get_user()
    if not user.is_authorized():
        return redirect(url_for('login.login'))


@module.get('/')
def admin_index():
    return redirect(url_for('admin.users_index'))


@module.get("/logout")
def logout():
    return redirect(url_for('admin.index'))
