from flask import (Blueprint, request, jsonify, current_app as app)

from feature_request.models import *
from feature_request.utils import InvalidUsage, to_datetime
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
        app.logger.error('Failed to get data for index page: %s' % Se)
        raise InvalidUsage('Failed to get feature requests', status_code=500)

    return RequestSchema().dumps(many=True, obj=client_requests).data


@bp.route('/api/v1/request/<int:req_id>', methods=('GET',))
def get_request(req_id: int):
    return RequestSchema().dumps(obj=_get_request(req_id)).data


@bp.route('/api/v1/request/create', methods=('POST',))
def create():
    """ Create new feature requests for the clients"""
    client_request_dict = _input_validation()

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
                client_request.client_priority = _get_priority()
                db.session.commit()
        except exc.SQLAlchemyError as Se:
            app.logger.error('Failed to save data for feature request:  %s' % Se)
            raise InvalidUsage('Unable create feature request', status_code=500)

        return success_response(status_code=201)


@bp.route('/api/v1/clients', methods=('GET',))
def get_clients():
    try:
        # get all clients
        clients = Client.query.all()

    except exc.SQLAlchemyError as Se:
        app.logger.error('Failed to get clients: %s' % Se)
        raise InvalidUsage('Failed to get clients')

    result = ClientSchema().dumps(many=True, obj=clients)

    return result.data, result.errors or 200


@bp.route('/api/v1/products', methods=('GET',))
def get_products():
    try:
        # get all products
        products = Product.query.all()

    except exc.SQLAlchemyError as Se:
        app.logger.error('Failed to get data for create page: %s' % Se)
        raise InvalidUsage('Failed to get clients')

    result = ProductSchema().dumps(many=True, obj=products)

    return result.data, result.errors or 200


def _get_priority():
    """ :return the priority for the current request """

    priority = db.session.query(db.func.max(Request.client_priority)).scalar()

    if priority:
        return priority + 1

    return 1


def _get_request(req_id: int):
    """
    :type req_id: int
    :return Feature request from the database by the request id

    """

    try:

        # get the feature request from the database
        client_request = Request.query.get(req_id)

        if not client_request:
            raise InvalidUsage('The Feature Request not found, id: %d' % req_id, status_code=404)

    except (exc.SQLAlchemyError, exc.DatabaseError, ValueError) as Se:
        # show internal server error if problem occurred with database connection
        app.logger.error('Failed get Feature request id:%d -> %s' % (req_id, Se))
        raise InvalidUsage('Failed to get Feature request id:%d -> internal error' % req_id, status_code=500)

    return client_request


@bp.route('/api/v1/request/<int:req_id>', methods=('DELETE',))
def delete(req_id: int):
    """
    the function will delete a feature request by it's id and will refresh the priority for all other feature requests
    :type req_id: int
    """
    client_request = _get_request(req_id)
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
        app.logger.error('Failed to delete request %d -> %s' % (req_id, Se))

        raise InvalidUsage('Failed to delete request id:%d' % req_id, status_code=500)

    return success_response()


def _input_validation():
    """
    :return the form as dict after validation
    """
    form = request.get_json(force=True)

    try:
        title = form['title']
        description = form['description']
        client_id = form['client_id']
        product_id = form['product_id']
        targeted_date = form['targeted_date']

        if not title:
            error = 'Title is required.'
            raise InvalidUsage('Bad Request: %s' % error, status_code=400)

        if len(title) > 250:
            error = 'Title is too long'
            raise InvalidUsage('Bad Request: %s' % error, status_code=400)

        if not description:
            error = 'Description is required.'
            raise InvalidUsage('Bad Request: %s' % error, status_code=400)

        if not client_id:
            error = 'Client is required.'
            raise InvalidUsage('Bad Request: %s' % error, status_code=400)

        if not product_id:
            error = 'Product is required.'
            raise InvalidUsage('Bad Request: %s' % error, status_code=400)

        if not targeted_date:
            error = 'Targeted Date is required.'
            raise InvalidUsage('Bad Request: %s' % error, status_code=400)

        else:
            targeted_date = to_datetime(targeted_date)
            if targeted_date < datetime.utcnow():
                error = 'Targeted date is old'
                raise InvalidUsage('Bad Request: %s' % error, status_code=400)

    except (KeyError, TypeError) as e:
        app.logger.warning('Input validation error: %s' % e)
        raise InvalidUsage('Bad Request', status_code=400)

    return dict(

        title=title,
        description=description,
        client_id=client_id,
        product_id=product_id,
        client_priority=_get_priority(),
        targeted_date=targeted_date

    )
