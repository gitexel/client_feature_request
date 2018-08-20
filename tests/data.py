from tests import TARGET_DATE
from feature_request.models import Request, Client, Product
from feature_request.db import db as _db
import pytest


@pytest.fixture(scope='module')
def init_db():
    _db.create_all()

    _db.session.add_all(
        [Client(name='Client A'), Client(name='Client B')]
    )

    _db.session.add_all(
        [Product(name='Policies'), Product(name='Billing')]
    )

    _db.session.add_all(
        [

            Request(
                title="hello2",
                description='Hello world2',
                client_id=2,
                product_id=2,
                client_priority=1,
                targeted_date=TARGET_DATE),

            Request(
                title="hello3",
                description='Hello world3',
                client_id=1,
                product_id=1,
                client_priority=2,
                targeted_date=TARGET_DATE)

        ]
    )

    _db.session.commit()

    return _db
