from app import create_app
from flask_script import Manager

app = create_app('dev')
manager = Manager(app)


@manager.command
def dev():
    app.run()


@manager.command
def pro():
    app.run('0.0.0.0')


if __name__ == '__main__':
    manager.run()
