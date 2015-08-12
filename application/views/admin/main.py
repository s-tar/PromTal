from flask import render_template, redirect, url_for

from application import Module

admin = Module('admin', __name__, url_prefix='/admin')


@admin.get('/')
def admin_index():
    return render_template('admin/index.html')


@admin.get("/logout")
def logout():
    return redirect(url_for('admin.index'))
