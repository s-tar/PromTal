from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

from application import db, create_app

app = create_app('default')
manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command("shell", Shell)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
