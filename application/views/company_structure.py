from application import Module, ldap, db
from flask import request, render_template, redirect, url_for, abort
from application.models.department import Department
from application.utils.datatables_sqlalchemy.datatables import row2dict


structure = Module('company_structure', __name__, url_prefix='/structure')

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

@structure.get("/show")
def show_structure():
    departments = get_departments()
    return render_template('company_structure/show.html', departments=departments)