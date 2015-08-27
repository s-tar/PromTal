from flask import render_template, request, current_app, url_for, redirect, jsonify

from application.views.admin.main import module
from application.models.user import User, Role, Permission
from application.models.department import Department
from application.models.view_users4search import ViewUsers4Search
from application import db, ldap
from application.utils.validator import Validator
from application.utils import auth
from application.bl.users import create_user, update_user, DataProcessingError
from application.utils.datatables_sqlalchemy.datatables import ColumnDT, DataTables


def _default_value(chain):
    return chain or '-'

def _empty(chain):
    return ''


def _default_value_view(chain):
    if chain == 'None':
        return None
    return chain


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

    current_user = auth.service.get_user()
    disabled = ''
    if not current_user.is_admin and ('set_permissions' not in current_user.get_permissions()):
        disabled = 'disabled'

    for row in json_result['aaData']:
        row_id = row['0']
        row['1'] = "<a href='"+url_for('user.profile')+"/"+row_id+"'>"+row['1']+"</a>"
        last_col = len(columns) - 1

        # Permission
        last_col += 1
        per_columns = str(last_col)
        per_options = ""
        permissions = Permission.get_all()
        set_per = User.get_user_permissions_id(row_id)
        for per in permissions:
            sel = ''
            sel = 'selected' if per.id in set_per else ''
            per_options += "<option value='"+str(per.id)+"' "+sel+">"+per.title+"</option>"
        per_html = """
          <select onchange="change_user_per("""+row_id+""", this)" class="selectpicker" multiple data-selected-text-format="count>1" data-width="170px" """+disabled+""">
            """+per_options+"""
          </select>
          <script type="text/javascript">$('.selectpicker').selectpicker({style: 'btn-default',size: 5});</script>
          """
        row[per_columns] = per_html

        # Roles
        last_col += 1
        roles_columns = str(last_col)
        roles = Role.get_all()
        role_options = ''
        sel_role = User.get_user_role_id(row_id)
        for role in roles:
            sel = ''
            sel = 'selected' if role.id == sel_role else ''
            role_options += "<option value='"+str(role.id)+"/"+row_id+"' "+sel+">"+role.name+"</option>"
        sel = ''
        sel = 'selected' if 0 == sel_role else ''
        role_options += "<option value='0/"+row_id+"' "+sel+">admin</option>"
        role_html = """
          <select onchange="change_user_role(this.value)" class="selectpicker" data-width="110px" """+disabled+""">
            """+role_options+"""
          </select>
          <script type="text/javascript">$('.selectpicker').selectpicker({style: 'btn-default',size: 5});</script>
          """
        row[roles_columns] = role_html

        # Manage
        last_col += 1
        last_columns = str(last_col)
        manage_html = """
            <a href="{edit_user_profile}">
                <span class="glyphicon glyphicon-pencil" aria-hidden="true"></span>
            </a>
            <a href="javascript: user.delete(%s)">
                <span class="glyphicon glyphicon-trash" aria-hidden="true"></span>
            </a>
        """ % row_id
        row[last_columns] = manage_html.format(
            edit_user_profile=url_for('admin.edit_user', id=row_id),
            delete_user_profile=url_for('admin.delete_user', id=row_id))
    return jsonify(**json_result)


@module.get('/users_search')
def users_search():
    return render_template('admin/users/users_search.html')


@module.get('/users_search_json')
def users_search_json():
    columns = list()
    columns.append(ColumnDT('users_id', filter=_default_value_view))
    columns.append(ColumnDT('users_full_name', filter=_default_value_view))
    columns.append(ColumnDT('users_login', filter=_empty))
    columns.append(ColumnDT('users_email', filter=_empty))
    columns.append(ColumnDT('users_status', filter=_empty))
    columns.append(ColumnDT('users_mobile_phone', filter=_empty))
    columns.append(ColumnDT('users_inner_phone', filter=_empty))
    columns.append(ColumnDT('users_birth_date', filter=_empty))
    columns.append(ColumnDT('users_skype', filter=_empty))
    columns.append(ColumnDT('users_position', filter=_empty))
    columns.append(ColumnDT('department_name', filter=_default_value_view))
    columns.append(ColumnDT('photo_url', filter=_default_value_view))
    return jsonify(**DataTables(request, ViewUsers4Search, db.session.query(ViewUsers4Search), columns).output_result())


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


@module.get('/users/edit/<int:id>')
def edit_user(id):
    user = User.query.get_or_404(id)
    groups = ldap.get_all_groups()
    departments = Department.query.all()
    return render_template('admin/users/edit_user.html',
                           user=user,
                           groups={group['cn'][0] for group in groups},
                           departments={department.name for department in departments})


@module.get('/users/add')
def add_user():
    groups = ldap.get_all_groups()
    departments = Department.query.all()
    return render_template('admin/users/add_user.html',
                           groups={group['cn'][0] for group in groups},
                           departments={department.name for department in departments})


@module.get('/users/set-user-role/<int:role_id>/<int:user_id>/')
def set_user_role(role_id, user_id):
    if role_id:
        User.set_user_role(user_id, role_id)
    else:
        User.set_user_is_admin(user_id)
    return jsonify({'status': 'ok'})


@module.get('/users/set-user-per/<int:user_id>/<per_string>/')
def set_user_per(user_id, per_string):
    User.set_user_per(user_id, per_string)
    return jsonify({'status': 'ok'})

