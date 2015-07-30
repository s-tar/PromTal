from flask import render_template, request, current_app, flash, url_for, redirect, jsonify, abort
from application.views.admin.main import admin
from application.models.department import Department
from application import db
from application.utils.datatables_sqlalchemy.datatables import row2dict
#import pprint


def get_departments(parent_id=None):
    dep_list = []
    departments = db.session.query(Department).filter_by(parent_id=parent_id).all()
    for dep in departments:
        dep_dict = row2dict(dep)
        dep_dict['dep_list'] = get_departments(dep.id)
        dep_list.append(dep_dict)
    if len(departments):
        return dep_list
    else:
        return None


@admin.get('/company_structure')
def company_structure():
    departments = get_departments()
    #pp = pprint.PrettyPrinter(indent=1)
    #pp.pprint(departments)
    return render_template('admin/company_structure/structure.html', departments=departments)