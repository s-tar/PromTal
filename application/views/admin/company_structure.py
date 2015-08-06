from flask import render_template, request, current_app, flash, url_for, redirect, jsonify, abort
from application.views.admin.main import admin
from application.models.department import Department
from application import db
from application.utils.datatables_sqlalchemy.datatables import row2dict
from application.utils.validator import Validator


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


@admin.get('/company-structure')
def company_structure():
    departments = get_departments()
    return render_template('admin/company_structure/structure.html', departments=departments)


@admin.get('/company-structure/edit/<int:dep_id>')
def edit_structure(dep_id):
    department = Department.get_by_id(dep_id)
    dep_parents = Department.get_parent_all(dep_id)
    return render_template('admin/company_structure/edit_structure.html',
                            department=department,
                            dep_parents = dep_parents)


@admin.post('/company-structure/edit-post/')
def edit_structure_post():
    v = Validator(request.form)
    v.field("name_structure").required()
    if v.is_valid():
        name_structure = v.valid_data.name_structure
        Department.rename(request.form.get("department_id"), name_structure)
        Department.set_parent(request.form.get("department_id"), request.form.get("parent"))
        print(request.form.get("parent"))
        return jsonify({"status": "ok"})
    return jsonify({"status": "fail",
                    "errors": v.errors})


@admin.get('/company-structure/add/<int:dep_id>')
def add_structure(dep_id):
    department = Department.get_by_id(dep_id)
    return render_template('admin/company_structure/add_structure.html', department=department)


@admin.post('/company-structure/add-post/')
def add_structure_post():
    v = Validator(request.form)
    v.field("name_structure").required()
    if v.is_valid():
        name_structure = v.valid_data.name_structure
        Department.add(request.form.get("department_id"), name_structure)
        return jsonify({"status": "ok"})
    return jsonify({"status": "fail",
                    "errors": v.errors})


@admin.get('/company-structure/delete/<int:dep_id>')
def delete_structure(dep_id):
    Department.delete(dep_id)
    return redirect(url_for('admin.company_structure'))