from requests_management.db import db
from datetime import datetime


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    requests = db.relationship('Request', back_populates='client')

    def __repr__(self):
        return '<Client %r>' % self.name


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    requests = db.relationship('Request', back_populates='product')

    def __repr__(self):
        return '<Product %r>' % self.name


class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    title = db.Column(db.String(250), nullable=False)
    description = db.Column(db.Text, nullable=False)

    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    client_priority = db.Column(db.Integer, unique=True, nullable=False)
    targeted_date = db.Column(db.DateTime, unique=True, nullable=False)

    client = db.relationship('Client', back_populates='requests')
    product = db.relationship('Product', back_populates='requests')

    def __repr__(self):
        return '<Request %r>' % self.title
