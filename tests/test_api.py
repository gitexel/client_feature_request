import dateparser
from feature_request.utils import from_date
from tests import *
import pytest

REQUEST_GET = {
    'id': 1,
    'title': 'hello2',
    'client': 2,
    'client_priority': 1,
    'targeted_date': from_date(TARGET_DATE),
    'description': 'Hello world2',
    'product': 2,
}

REQUEST_POST = {
    'title': 'hello4',
    'client_id': 1,
    'targeted_date': from_date(TARGET_DATE),
    'description': 'Hello world4',
    'product_id': 2,
}

CLIENTS = [{'id': 1, 'name': 'Client A'}, {'id': 2, 'name': 'Client B'}]
PRODUCTS = [{'id': 1, 'name': 'Policies'}, {'id': 2, 'name': 'Billing'}]


@pytest.mark.xfail(raises=(KeyError, IndexError))
def test_request_all(client):
    response = client.get('/api/v1/request/all')

    cleaned_json = json_of_response(response)[0]
    del cleaned_json['created']
    targeted_date = dateparser.parse(cleaned_json['targeted_date'])
    cleaned_json['targeted_date'] = from_date(targeted_date)
    assert response.status_code == 200
    assert cleaned_json == REQUEST_GET


@pytest.mark.xfail(raises=IndexError)
def test_get_clients(client):
    response = client.get('/api/v1/clients')
    cleaned_json = json_of_response(response)

    assert response.status_code == 200
    assert cleaned_json[0] == CLIENTS[0]
    assert cleaned_json[1] == CLIENTS[1]


@pytest.mark.xfail(raises=IndexError)
def test_get_products(client):
    response = client.get('/api/v1/products')
    cleaned_json = json_of_response(response)

    assert response.status_code == 200
    assert cleaned_json[0] == PRODUCTS[0]
    assert cleaned_json[1] == PRODUCTS[1]


@pytest.mark.xfail(raises=KeyError)
def test_get_feature_request_by_id(client):
    response = client.get('/api/v1/request/1')
    assert response.status_code == 200
    cleaned_json = json_of_response(response)
    del cleaned_json['created']
    targeted_date = dateparser.parse(cleaned_json['targeted_date'])
    cleaned_json['targeted_date'] = from_date(targeted_date)
    assert cleaned_json == REQUEST_GET


def test_get_feature_request_with_not_exist_id(client):
    response = client.get('/api/v1/request/1000')
    assert response.status_code == 404


@pytest.mark.xfail(raises=KeyError)
def test_post_new_request(client):
    response = post_json(client, '/api/v1/request/', REQUEST_POST)
    cleaned_json = json_of_response(response)
    assert response.status_code == 201
    assert cleaned_json['success'] is True


@pytest.mark.xfail(raises=KeyError)
def test_post_new_request_with_old_date(client):
    feature_request = REQUEST_POST.copy()
    feature_request['targeted_date'] = from_date(TARGET_DATE_OLD)
    response = post_json(client, '/api/v1/request/', feature_request)
    cleaned_json = json_of_response(response)

    assert response.status_code == 400
    assert 'Targeted date is old' in cleaned_json['message']


@pytest.mark.xfail(raises=KeyError)
def test_post_new_request_with_missing_required_fields(client):
    feature_request = REQUEST_POST.copy()
    feature_request['targeted_date'] = from_date(TARGET_DATE_OLD)
    del feature_request['title']
    response = post_json(client, '/api/v1/request/', feature_request)
    cleaned_json = json_of_response(response)

    assert response.status_code == 400
    assert 'Bad Request' in cleaned_json['message']


@pytest.mark.xfail(raises=KeyError)
def test_post_new_request_with_an_empty_required_fields(client):
    feature_request = REQUEST_POST.copy()
    feature_request['title'] = ''
    response = post_json(client, '/api/v1/request/', feature_request)
    cleaned_json = json_of_response(response)

    assert response.status_code == 400
    assert 'Title is required' in cleaned_json['message']


@pytest.mark.xfail(raises=(KeyError, IndexError))
def test_post_new_request_and_priority_effect(client):
    response = client.get('/api/v1/request/all')
    cleaned_json = json_of_response(response)[-1]
    assert response.status_code == 200
    priority = cleaned_json['client_priority']

    # post new feature request
    response = post_json(client, '/api/v1/request/', REQUEST_POST)
    cleaned_json = json_of_response(response)
    assert response.status_code == 201
    assert cleaned_json['success'] is True

    # get the recent posted request should have priority with +1
    response = client.get('/api/v1/request/all')
    cleaned_json = json_of_response(response)[-1]
    assert response.status_code == 200
    assert cleaned_json['client_priority'] == priority + 1


@pytest.mark.xfail(raises=KeyError)
def test_delete_feature_request_not_exits(client):
    response = client.get('/api/v1/request/12020')
    assert response.status_code == 404


@pytest.mark.xfail(raises=KeyError)
def test_delete_feature_request_only(client):
    response = client.delete('/api/v1/request/1')
    cleaned_json = json_of_response(response)

    assert response.status_code == 200
    assert cleaned_json['success'] is True

    response = client.get('/api/v1/request/all')
    assert response.status_code == 200

    assert len(json_of_response(response)) == 3

    response = client.get('/api/v1/request/1')
    assert response.status_code == 404


@pytest.mark.xfail(raises=KeyError)
def test_delete_and_priority_effect(client):
    # get the first feature request id =2 should have priority = 1
    response = client.get('/api/v1/request/2')
    assert response.status_code == 200
    cleaned_json = json_of_response(response)
    assert cleaned_json['client_priority'] == 1

    # delete request with id =2
    response = client.delete('/api/v1/request/2')
    cleaned_json = json_of_response(response)

    assert response.status_code == 200
    assert cleaned_json['success'] is True

    # get feature request id = 3 should have priority = 1 after deleting the previous request
    response = client.get('/api/v1/request/3')
    assert response.status_code == 200
    cleaned_json = json_of_response(response)
    assert cleaned_json['client_priority'] == 1
