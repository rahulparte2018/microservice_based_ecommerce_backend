# product_management_service/tests/app_test.py
import datetime
import pytest
from product_management_service.app import app, db, Product
from flask import json
from common.jwt_middleware import SECRET_KEY
import jwt

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def get_token(user_id):
    return jwt.encode({'user_id': user_id, 'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=24)}, SECRET_KEY)

def test_get_products(client):
    token = get_token(1)
    headers = {'x-access-token': token}
    response = client.get('/products', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)

def test_update_product(client):
    token = get_token(1)
    headers = {'x-access-token': token}
    product = Product(name='Test Product', description='Test Description', price=10.0, stock=100, version=1)
    with app.app_context():
        db.session.add(product)
        db.session.commit()
    response = client.put('/products/1', data=json.dumps({'name': 'Updated Product', 'description': 'Updated Description', 'price': 15.0, 'stock': 50, 'version': 1}), content_type='application/json', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'product updated successfully'

def test_update_product_version_conflict(client):
    token = get_token(1)
    headers = {'x-access-token': token}
    product = Product(name='Test Product', description='Test Description', price=10.0, stock=100, version=1)
    with app.app_context():
        db.session.add(product)
        db.session.commit()
    response = client.put('/products/1', data=json.dumps({'name': 'Updated Product', 'description': 'Updated Description', 'price': 15.0, 'stock': 50, 'version': 2}), content_type='application/json', headers=headers)
    assert response.status_code == 409
    data = json.loads(response.data)
    assert data['message'] == 'version conflict'
