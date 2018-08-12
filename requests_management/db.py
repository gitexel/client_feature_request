import click
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy db
db = None


def init_db():
    db.create_all()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """create new tables if not exist"""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    global db
    app.cli.add_command(init_db_command)
    db = SQLAlchemy(app)
    db.init_app(app)
