from flask import render_template, request, current_app, flash, url_for, redirect, jsonify, abort
from application.views.admin.main import admin


@admin.get('/company_structure')
def company_structure():
    return render_template('admin/company_structure/structure.html')