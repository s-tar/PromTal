from flask import render_template, request, current_app, flash, url_for, redirect, jsonify, abort

from application.views.admin.main import admin
from application.models.user import User
from application.forms.admin.user import EditUserForm
from application import db, ldap
from application.utils.validator import Validator
from application.bl.admin import add_user_data_to_db
from application.utils.datatables_sqlalchemy.datatables import ColumnDT, DataTables


@admin.get('/users_list')
def users_list():
    users = User.query.order_by(User.full_name.asc()).all()
    return render_template('admin/users/users.html', users=users)


@admin.get('/users_list_sql')
def users_list_sql():
    users = User.query.order_by(User.full_name.asc()).all()
    return render_template('admin/users/users_sql.html', users=users)


@admin.get('/simple_example')
def simple_example():
    # defining columns
    columns = []
    columns.append(ColumnDT('full_name'))
    columns.append(ColumnDT('login'))
    columns.append(ColumnDT('email'))
    

    # defining the initial query depending on your purpose
    query = db.session.query(User)
    #print("\nquery.all() =", len(query), "\n")
    #row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
    #rezalt = []
    #for i in query:
    #    print(row2dict(i))
    #print("\nquery.all() =", query.all().__dict__, "\n")

    # instantiating a DataTable for the query and table needed
    rowTable = DataTables(request, User, query, columns)
    a = rowTable.output_result()
    #print("\n\n\n", a, "\n\n\n")
    # returns what is needed by DataTable
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
@admin.post('/users/edit/<int:id>')
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
    v.field('mobile_phone').required()
    if v.is_valid():
        data = {
            'name': request.form.get('name'),
            'surname': request.form.get('surname'),
            'email': request.form.get('email'),
            'login': request.form.get('login'),
            'department': request.form.get('department'),
            'groups': request.form.get('groups'),
            'mobile_phone': request.form.get('mobile_phone')
        }

        if User.get_by_login(data['login']):
            pass
        elif User.get_by_email(data['email']):
            pass

        add_user_data_to_db(data)

        return jsonify({"status": "ok"})
    return jsonify({"status": "fail",
                    "errors": v.errors})
