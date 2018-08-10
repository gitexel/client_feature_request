from datetime import datetime
from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from requests_management.db import db
from requests_management.models import Request, Client, Product

bp = Blueprint('request', __name__)


@bp.route('/')
def index():
    client_requests = Request.query.join(
        Product, Request.product_id == Product.id).join(Client, Client.id == Request.client_id).all()

    return render_template('index.html', client_requests=client_requests, today=datetime.today())


@bp.route('/request/create', methods=('GET', 'POST'))
def create():
    clients = Client.query.all()
    products = Product.query.all()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        client_id = request.form['client_id']
        product_id = request.form['product_id']
        targeted_date = datetime.strptime(request.form['targeted_date'], '%Y-%m-%d')
        client_priority = get_priority()

        error = None

        if not title:
            error = 'Title is required.'

        if targeted_date < datetime.today():
            error = 'Targeted date is old'

        if error is not None:
            flash(error)
        else:

            client_request = Request(

                title=title,
                description=description,
                client_id=client_id,
                product_id=product_id,
                client_priority=client_priority,
                targeted_date=targeted_date
            )
            db.session.add(client_request)
            db.session.commit()
            return redirect(url_for('index'))

    return render_template('create.html', clients=clients, products=products,
                           today=datetime.today().strftime('%Y-%m-%d'))


def get_priority():
    priority = db.session.query(db.func.max(Request.client_priority)).scalar()
    if priority:
        return priority + 1

    return 1


def get_request(req_id):
    client_request = Request.query.join(
        Product, Request.product_id == Product.id).join(Client, Client.id == Request.client_id).filter(
        Request.id == req_id).one()

    if client_request is None:
        abort(404, "Post id {0} doesn't exist.".format(req_id))

    return client_request


@bp.route('/request/<int:req_id>/update', methods=('GET', 'POST'))
def update(req_id):
    client_request = get_request(req_id)
    clients = Client.query.all()
    products = Product.query.all()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:

            if client_request.title != title or client_request.description != description:
                client_request.description = description
                client_request.title = title
                db.session.commit()

            return redirect(url_for('index'))

    return render_template('update.html', clients=clients, products=products, client_request=client_request)


@bp.route('/request/<int:req_id>/delete', methods=('POST',))
def delete(req_id):
    client_request = get_request(req_id)
    client_priority = client_request.client_priority
    db.session.delete(client_request)
    db.session.commit()
    for client_req in Request.query.filter(Request.client_priority > client_priority):
        client_req.client_priority -= 1

    db.session.commit()

    return redirect(url_for('index'))
