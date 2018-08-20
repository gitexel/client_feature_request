from datetime import datetime
from flask import current_app as app

DATE_FORMAT = '%Y-%m-%d'


# DATE_FORMAT = app.config.get('DATE_FORMAT')


def to_datetime(value):
    return datetime.strptime(value, DATE_FORMAT)


def to_date(value):
    return datetime.strptime(value, DATE_FORMAT).date()


def from_date(value):
    return datetime.strftime(value, DATE_FORMAT)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = self.status_code
        return rv
