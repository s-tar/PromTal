from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

from application import db, create_app
from application.models.user import Permission, Role

app = create_app('default')
manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command("shell", Shell)
manager.add_command('db', MigrateCommand)


@manager.command
def sync_permissions():
    for name, title in Permission.PERMISSIONS:
        permission = Permission.query.filter_by(name=name).first()
        if permission is None:
            p = Permission()
            p.name = name
            p.title = title
            db.session.commit()


@manager.command
def insert_roles():
    roles = {
        'user': ['post_comment'],
        'moderator': ['edit_comments', 'write_articles', 'moderate_comments', 'manage_users', 'set_permissions']
    }
    permissions_map = {p.name: p for p in Permission.query}

    for role, permissions in roles.items():
        ur = Role.query.filter_by(name=role).first()
        if ur is None:
            r = Role()
            for p in permissions:
                r.permissions.append(permissions_map.get(p))
            r.name = role
            db.session.add(r)
            db.session.commit()


if __name__ == '__main__':
    manager.run()
