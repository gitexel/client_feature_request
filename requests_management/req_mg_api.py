from flask import (Blueprint, request, current_app, jsonify)

from requests_management import InvalidUsage
from requests_management.models import *
from sqlalchemy import exc

bp = Blueprint('api', __name__)


def success_response(status_code=200):
    return jsonify({
        'success': True,
        'status': status_code
    }), status_code, {'ContentType': 'application/json'}


@bp.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """Handel API errors"""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@bp.route('/api/v1/request/all', methods=('GET',))
def all_requests():
    try:

        # get all feature requests from the database
        client_requests = Request.query.all()
    except (exc.SQLAlchemyError, exc.DatabaseError, ValueError) as Se:
        current_app.logger.error('Failed to get data for index page: %s' % Se)
        raise InvalidUsage('Failed to get data for index page', status_code=500)

    return RequestSchema().dumps(many=True, obj=client_requests).data


@bp.route('/api/v1/request/', methods=('POST', 'GET'))
def create():
    """ Create new feature requests for the clients"""

    client_request_dict = input_validation(form=request.json)

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
            raise InvalidUsage('Unable create feature request', status_code=500)

        return success_response(status_code=201)


@bp.route('/api/v1/clients', methods=('GET',))
def get_clients():
    try:
        # get all clients
        clients = Client.query.all()

    except exc.SQLAlchemyError as Se:
        current_app.logger.error('Failed to get clients: %s' % Se)
        raise InvalidUsage('Failed to get clients')

    result = ClientSchema().dumps(many=True, obj=clients)

    return result.data, result.errors or 200


@bp.route('/api/v1/products', methods=('GET',))
def get_products():
    try:
        # get all clients
        products = Product.query.all()

    except exc.SQLAlchemyError as Se:
        current_app.logger.error('Failed to get data for create page: %s' % Se)
        raise InvalidUsage('Failed to get clients')

    result = ProductSchema().dumps(many=True, obj=products)

    return result.data, result.errors or 200


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

    try:

        # get the feature request from the database
        client_request = Request.query.filter(Request.id == req_id).first()

        if not client_request:
            raise InvalidUsage('Failed to get Feature request id:%d' % req_id, status_code=404)

    except (exc.SQLAlchemyError, exc.DatabaseError, ValueError) as Se:
        # show internal server error if problem occurred with database connection
        current_app.logger.error('Failed get Feature request id:%d -> %s' % (req_id, Se))
        raise InvalidUsage('Failed to get Feature request id:%d -> internal error' % req_id, status_code=500)

    return client_request


@bp.route('/api/v1/request/<int:req_id>', methods=('DELETE',))
def delete(req_id: int):
    """
    the function will delete a feature request by it's id and will refresh the priority for all other feature requests
    :type req_id: int
    """
    client_request = get_request(req_id)
    client_priority = client_request.client_priority
    db.session.delete(client_request)

    try:

        # subtract all feature requests that have high priority of the deleted item
        for client_req in Request.query.filter(Request.client_priority > client_priority):
            client_req.client_priority -= 1

        db.session.commit()

    except exc.SQLAlchemyError as Se:

        db.session.rollback()

        # show internal server error if problem occurred with database connection
        current_app.logger.error('Failed to delete request %d -> %s' % (req_id, Se))

        raise InvalidUsage('Failed to delete request id:%d' % req_id, status_code=500)

    return success_response()


def input_validation(form: dict):
    """
    :return the form as dict after validation
    :type form: dict
    """
    error = None

    try:
        title = form['title']
        description = form['description']
        client_id = form['client_id']
        product_id = form['product_id']
        targeted_date = form['targeted_date']

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
            raise InvalidUsage(error, status_code=400)

    except (KeyError, TypeError) as e:
        current_app.logger.warning('Input validation error: %s' % e)
        raise InvalidUsage('Bad Request', status_code=400)

    return dict(

        title=title,
        description=description,
        client_id=client_id,
        product_id=product_id,
        client_priority=get_priority(),
        targeted_date=targeted_date

    )
