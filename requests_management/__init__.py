import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev-key-123',
        SQLALCHEMY_DATABASE_URI=os.path.join('sqlite:////' + app.instance_path, 'req_mg.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=True
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError as Eos:
        app.logger.info('Failed to create instance folder: %s' % Eos)

    from . import db
    db.init_app(app)

    from . import req_mg
    # add request page
    app.register_blueprint(req_mg.bp)
    app.add_url_rule('/', endpoint='index')

    return app
