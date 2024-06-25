# order_processing_service/tests/app_test.py
import datetime
import pytest
from order_processing_service.app import app, db, Order
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

def test_create_order(client):
    token = get_token(1)
    headers = {'x-access-token': token}
    response = client.post('/orders', data=json.dumps({'product_id': 1, 'quantity': 10}), content_type='application/json', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'order created successfully'
