from application import Module
from flask import render_template

module = Module('admin', __name__, url_prefix='/admin')

@module.get('/')
def admin_index():
    return render_template('admin/index.html')