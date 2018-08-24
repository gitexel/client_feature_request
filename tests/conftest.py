import os
import tempfile
import pytest
from feature_request import create_app


@pytest.fixture(scope='module')
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': os.path.join('sqlite:////' + db_path),
        'DATE_FORMAT': '%Y-%m-%d',
    })
    # Establish an application context before running the tests.
    with app.app_context():
        import tests.data as data
        _db = data.init_db()

    yield app

    with app.app_context():
        _db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope='module')
def client(app):
    return app.test_client()


@pytest.fixture(scope='module')
def runner(app):
    return app.test_cli_runner()
