import click
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.exc import SQLAlchemyError

# SQLAlchemy db
db = SQLAlchemy()

# marshmallow
ma = Marshmallow()


def init_db():
    db.create_all()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """create new tables if not exist"""
    try:
        init_db()
        click.echo('Initialized the database.')
    except SQLAlchemyError as Se:
        click.echo('Can\'t create db: %s' % Se)


def init_app(app):
    app.cli.add_command(init_db_command)
    db.init_app(app)
