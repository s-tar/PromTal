from application import Module
from flask import render_template, redirect, url_for

admin = Module('admin', __name__, url_prefix='/admin')


@admin.get('/')
def admin_index():
    return render_template('admin/index.html')


@admin.route("/logout")
def logout():
    return redirect(url_for('admin.index'))