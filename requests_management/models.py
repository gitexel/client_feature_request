from requests_management.db import db, ma
from datetime import datetime


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Client %r>' % self.name


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Product %r>' % self.name


class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    title = db.Column(db.String(250), nullable=False)
    description = db.Column(db.Text, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    client_priority = db.Column(db.Integer, unique=True, nullable=False)
    targeted_date = db.Column(db.DateTime, nullable=False)

    client = db.relationship('Client')
    product = db.relationship('Product')

    def __init__(self, title, description, client_id, product_id, client_priority, targeted_date):
        self.title = title
        self.description = description
        self.client_id = client_id
        self.product_id = product_id
        self.client_priority = client_priority
        self.targeted_date = targeted_date

    def __repr__(self):
        return '<Request %r>' % self.title


class RequestSchema(ma.ModelSchema):
    class Meta:
        model = Request


class ClientSchema(ma.ModelSchema):
    class Meta:
        model = Client


class ProductSchema(ma.ModelSchema):
    class Meta:
        model = Product
