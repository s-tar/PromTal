from datetime import datetime
from flask import render_template, request, current_app, flash, url_for, redirect, jsonify

from application.views.admin.main import module
from application.models.user import User
from application.models.department import Department
from application import db, ldap
from application.utils.validator import Validator
from application.bl.users import create_user, update_user, DataProcessingError
from application.utils.datatables_sqlalchemy.datatables import ColumnDT, DataTables


def _default_value(chain):
    return chain or '-'


@module.get('/users_list')
def users_list():
    users = User.query.order_by(User.full_name.asc()).all()
    return render_template('admin/users/users.html', users=users)


@module.get('/users')
def users_index():
    users = User.query.order_by(User.full_name.asc())
    page = request.args.get('page', 1, type=int)
    pagination = users.paginate(
        page,
        per_page=current_app.config['ADMIN_USERS_PER_PAGE'],
        error_out=False
    )
    users = pagination.items
    return render_template(
        'admin/users/index.html',
        users=users,
        pagination=pagination
    )


@module.get('/s_users')
def s_users():
    return render_template('admin/users/s_users.html')


@module.get('/s_users_json')
def s_users_json():
    columns = list()
    columns.append(ColumnDT('id', filter=_default_value))
    columns.append(ColumnDT('full_name', filter=_default_value))
    columns.append(ColumnDT('email', filter=_default_value))
    columns.append(ColumnDT('login', filter=_default_value))
    columns.append(ColumnDT('mobile_phone', filter=_default_value))
    columns.append(ColumnDT('inner_phone', filter=_default_value))
    query = db.session.query(User)
    rowTable = DataTables(request, User, query, columns)
    json_result = rowTable.output_result()
    for row in json_result['aaData']:
        row_id = row['0']
        row['1'] = "<a href='"+url_for('user.profile')+"/"+row_id+"'>"+row['1']+"</a>"
        last_columns = str(len(columns))
        manage_html = """
            <a href="{edit_user_profile}">
                <span class="glyphicon glyphicon-pencil" aria-hidden="true"></span>
            </a>
            <a href="{delete_user_profile}">
                <span class="glyphicon glyphicon-trash" aria-hidden="true"></span>
            </a>
        """
        row[last_columns] = manage_html.format(
            edit_user_profile = url_for('admin.edit_user', id=row_id),
            delete_user_profile = url_for('admin.delete_user', id=row_id))
    return jsonify(**json_result)


@module.get('/users/edit/<int:id>')
def edit_user(id):
    user = User.get_by_id(id)
    departments = Department.query.all()
    return render_template('admin/users/edit_user_profile.html',
                           user=user,
                           departments={department.name for department in departments})


@module.post('/users/edit/<int:id>')
def edit_user_post(id):
    user = User.get_by_id(id)
    data = dict(request.form)
    data["file"] = request.files["file"]

    v = Validator(data)
    v.field('full_name').required()
    v.field('email').required().email()
    v.field('mobile_phone').required().phone_number()
    v.field('inner_phone').required()
    v.field('department').required()
    v.field('birth_date').datetime(format="%d.%m.%Y")
    v.field('file').image()
    if v.is_valid():
        data = {
            'login': user.login,
            'full_name': v.valid_data.full_name,
            'mobile_phone': v.valid_data.mobile_phone,
            'inner_phone': v.valid_data.inner_phone,
            'department': v.valid_data.department,
            'email': v.valid_data.email,
            'skype': v.valid_data.skype,
            'photo': v.valid_data.photo,
            'birth_date': v.valid_data.birth_date
        }

        try:
            update_user(**data)
            return jsonify({"status": "ok"})
        except DataProcessingError as e:
            return jsonify({'status': 'failOnProcess',
                            'error': e.value})

    return jsonify({"status": "fail",
                    "errors": v.errors})


@module.get('/users/delete/<int:id>')
def delete_user(id):
    user = User.query.get_or_404(id)
    user.status = User.STATUS_DELETED
    db.session.commit()
    return redirect(url_for('admin.users_index'))


@module.get('/users/activate/<int:id>')
def activate_user(id):
    user = User.query.get_or_404(id)
    user.status = User.STATUS_ACTIVE
    db.session.commit()
    return redirect(url_for('admin.users_index'))


@module.get('/users/block/<int:id>')
def block_user(id):
    user = User.query.get_or_404(id)
    user.status = User.STATUS_BLOCKED
    db.session.commit()
    return redirect(url_for('admin.users_index'))


@module.get('/users/add')
def add_user():
    groups = ldap.get_all_groups()
    departments = Department.query.all()
    return render_template('admin/users/add_user_profile.html',
                           groups={group['cn'][0] for group in groups},
                           departments={department.name for department in departments})


@module.post('/users/add')
def add_user_post():
    v = Validator(request.form)
    v.field('name').required()
    v.field('surname').required()
    v.field('email').required().email()
    v.field('login').required()
    v.field('department').required()
    v.field('groups').required()
    v.field('mobile_phone').required().phone_number()
    if v.is_valid():
        data = {
            'name': v.valid_data.name,
            'surname': v.valid_data.surname,
            'email': v.valid_data.email,
            'login': v.valid_data.login,
            'department': v.valid_data.department,
            'groups': v.valid_data.list('groups'),
            'mobile_phone': v.valid_data.mobile_phone
        }

        already_used_login = User.get_by_login(data['login'])
        already_used_email = User.get_by_email(data['email'])

        if already_used_login:
            v.add_error('login', 'Такой логин уже занят')
        if already_used_email:
            v.add_error('email', 'Такой email уже занят')

        if already_used_login or already_used_email:
            return jsonify({"status": "fail",
                            "errors": v.errors})

        try:
            create_user(**data)
            return jsonify({"status": "ok"})
        except DataProcessingError as e:
            return jsonify({'status': 'failOnProcess',
                            'error': e.value})

    return jsonify({"status": "fail",
                    "errors": v.errors})
