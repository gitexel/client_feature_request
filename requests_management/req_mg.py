from datetime import datetime

from werkzeug.datastructures import ImmutableDict
from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort

from requests_management.db import db
from requests_management.models import Request, Client, Product
from sqlalchemy import exc

bp = Blueprint('request', __name__)


@bp.route('/')
def index():
    """ the index of the website that show all feature requests """

    client_requests = None

    try:
        # get all feature requests from the database
        client_requests = Request.query.join(
            Product, Request.product_id == Product.id).join(Client, Client.id == Request.client_id).all()
        raise exc.SQLAlchemyError
    except exc.SQLAlchemyError as Se:
        current_app.logger.error('Failed to get data for index page: %s' % Se)

    return render_template('index.html', client_requests=client_requests, today=datetime.today())


@bp.route('/request/create', methods=('GET', 'POST'))
def create():
    """ Create new feature requests for the clients"""

    clients, products = get_pre_data_for_html_page()

    if not clients or not products:
        abort(503, "Create feature request is not available, please try again later")

    if request.method == 'POST':

        client_request_dict = input_validation(form=request.form)

        if client_request_dict:

            # get the new feature request after validating inputs
            client_request = Request(**client_request_dict)
            # add the object to the database session
            db.session.add(client_request)

            try:
                try:
                    # commit the new request to database
                    db.session.commit()
                except exc.IntegrityError:
                    db.session.rollback()
                    # get the most recent priority if we faced an integrity error
                    client_request.client_priority = get_priority()
                    db.session.commit()
            except exc.SQLAlchemyError as Se:
                current_app.logger.error('Failed to save data for feature request:  %s' % Se)

            return redirect(url_for('index'))

    return render_template('create.html', clients=clients, products=products,
                           today=datetime.today().strftime('%Y-%d-%m'))


def get_pre_data_for_html_page():
    clients, products = None, None

    try:
        # get all clients and products
        clients = Client.query.all()
        products = Product.query.all()

    except exc.SQLAlchemyError as Se:
        current_app.logger.error('Failed to get data for create page: %s' % Se)

    return clients, products


def get_priority():
    """ :return the priority for the current request """

    priority = db.session.query(db.func.max(Request.client_priority)).scalar()

    if priority:
        return priority + 1

    return 1


def get_request(req_id: int):
    """
    :type req_id: int
    :return Feature request from the database by the request id

    """

    client_request = None

    try:

        # get the feature request from the database
        client_request = Request.query.join(
            Product, Request.product_id == Product.id).join(Client, Client.id == Request.client_id).filter(
            Request.id == req_id).one()

        if client_request is None:
            # show abort page if the feature request doesn't exist
            abort(404, "Feature Request id %d doesn't exist." % req_id)

    except exc.SQLAlchemyError as Se:
        # show internal server error if problem occurred with database connection
        abort(500, 'Failed get Feature request id:%d' % req_id)
        current_app.logger.error('Failed get Feature request id:%d -> %s' % (req_id, Se))

    return client_request


@bp.route('/request/<int:req_id>/update', methods=('GET', 'POST'))
def update(req_id: int):
    """
    this function will update a feature request by it's id
    :type req_id: int
    """
    client_request = get_request(req_id)

    clients, products = get_pre_data_for_html_page()

    if request.method == 'POST':

        client_request_new = input_validation(form=request.form)

        if client_request_new:

            if client_request.title != client_request_new['title']:
                client_request.title = client_request_new['title']

            if client_request.description != client_request_new['description']:
                client_request.description = client_request_new['description']

            if client_request.client_id != client_request_new['client_id']:
                client_request.client_id = client_request_new['client_id']

            if client_request.product_id != client_request_new['product_id']:
                client_request.product_id = client_request_new['product_id']

            if client_request.targeted_date != client_request_new['targeted_date']:
                client_request.targeted_date = client_request_new['targeted_date']

            try:
                # commit changes to the database
                db.session.commit()

            except exc.SQLAlchemyError as Se:

                # show internal server error if problem occurred with database connection
                current_app.logger.error('Failed to update feature request %d -> %s' % (req_id, Se))
                abort(500, 'Failed to update feature request %d:%s' % (req_id, client_request.title))

            return redirect(url_for('index'))

    return render_template('update.html', clients=clients, products=products, client_request=client_request)


@bp.route('/request/<int:req_id>/delete', methods=('POST',))
def delete(req_id: int):
    """
    the function will delete a feature request by it's id and will refresh the priority for all other feature requests
    :type req_id: int
    """
    client_request = get_request(req_id)
    client_priority = client_request.client_priority
    db.session.delete(client_request)

    try:

        # subtract all feature requests that have high priority of the delete item
        for client_req in Request.query.filter(Request.client_priority > client_priority):
            client_req.client_priority -= 1

        db.session.commit()

    except exc.SQLAlchemyError as Se:

        db.session.rollback()

        # show internal server error if problem occurred with database connection
        current_app.logger.error('Failed to delete request %d -> %s' % (req_id, Se))

        abort(500, 'Failed to delete request %d:%s' % (client_request.id, client_request.title))

    return redirect(url_for('index'))


def input_validation(form: ImmutableDict):
    """
    :return the form as dict after validation
    :type form: ImmutableDict
    """
    error = None

    title = form.get('title', '').strip()
    description = form.get('description', '').strip()
    client_id = form.get('client_id', None)
    product_id = form.get('product_id', None)
    targeted_date = form.get('targeted_date', None)

    if not title:
        error = 'Title is required.'

    if not description:
        error = 'Description is required.'

    if not client_id:
        error = 'Client is required.'

    if not product_id:
        error = 'Product is required.'

    if not targeted_date:
        error = 'Targeted Date is required.'
    else:
        targeted_date = datetime.strptime(targeted_date, '%Y-%m-%d')
        if targeted_date < datetime.today():
            error = 'Targeted date is old'

    if error is not None:
        # show the errors to the current page
        flash(error)
        return False

    return dict(

        title=title,
        description=description,
        client_id=client_id,
        product_id=product_id,
        client_priority=get_priority(),
        targeted_date=targeted_date

    )
