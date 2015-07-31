from flask import render_template, request, current_app, flash, url_for, redirect, jsonify, abort

from application.views.admin.main import admin
from application.models.user import User
from application.forms.admin.user import EditUserForm
from application import db, ldap
from application.utils.validator import Validator
from application.bl.admin import add_user_data_to_db
from application.utils.datatables_sqlalchemy.datatables import ColumnDT, DataTables


def _default_value(chain):
    return chain or '-'


@admin.get('/users_list')
def users_list():
    users = User.query.order_by(User.full_name.asc()).all()
    return render_template('admin/users/users.html', users=users)


@admin.get('/s_users')
def s_users():
    return render_template('admin/users/s_users.html')


@admin.get('/s_users_json')
def s_users_json():
    columns = []
    columns.append(ColumnDT('id', filter=_default_value))
    columns.append(ColumnDT('full_name', filter=_default_value))
    columns.append(ColumnDT('email', filter=_default_value))
    columns.append(ColumnDT('login', filter=_default_value))
    columns.append(ColumnDT('mobile_phone', filter=_default_value))
    columns.append(ColumnDT('inner_phone', filter=_default_value))
    query = db.session.query(User)
    rowTable = DataTables(request, User, query, columns)
    a = rowTable.output_result()
    for i in a['aaData']:
        row_id = i['0']
        last_columns = str(len(columns))
        manage_html = """
            <a href="{edit_user_profile}">
                <span class="glyphicon glyphicon-pencil" aria-hidden="true"></span>
            </a>
            <a href="{delete_user_profile}">
                <span class="glyphicon glyphicon-trash" aria-hidden="true"></span>
            </a>
        """
        i[last_columns] = manage_html.format(
            edit_user_profile = url_for('admin.edit_user_profile', id=row_id),
            delete_user_profile = url_for('admin.delete_user_profile', id=row_id))
    return jsonify(**a)


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
    return render_template(
        'admin/users/index.html',
        users=users,
        pagination=pagination
    )


@admin.get('/users/edit/<int:id>')
def edit_user_profile(id):
    user = User.get_by_id(id)
    form = EditUserForm()
    if form.validate_on_submit():
        user.full_name = form.full_name.data
        user.mobile_phone = form.mobile_phone.data
        user.inner_phone = form.inner_phone.data
        user.birth_date = form.birth_date.data
        user.avatar = form.avatar.data
        user.skype = form.skype.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('admin.users_index'))
    form.full_name.data = user.full_name
    form.mobile_phone.data = user.mobile_phone
    form.inner_phone.data = user.inner_phone
    form.birth_date.data = user.birth_date
    form.avatar.data = user.avatar
    form.skype.data = user.skype
    return render_template(
        'admin/users/edit_user_profile.html',
        form=form,
        user=user
    )


@admin.get('/users/delete/<int:id>')
def delete_user_profile(id):
    user = User.get_by_id(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin.users_index'))


@admin.get('/users/add')
def add_user():
    groups = ldap.get_all_groups()
    departments = {'This is a mock', 'This is also a mock', 'One more'}  # TODO replace
    return render_template('admin/users/add_user_profile.html',
                           groups={group['cn'][0] for group in groups},
                           departments=departments)


@admin.post('/users/add')
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

        add_user_data_to_db(data)

        return jsonify({"status": "ok"})
    return jsonify({"status": "fail",
                    "errors": v.errors})
