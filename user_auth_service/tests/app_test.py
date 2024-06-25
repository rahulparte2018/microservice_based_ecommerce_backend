# user_auth_service/tests/app_test.py
import pytest
from user_auth_service.app import app, db, User
from flask import json
from werkzeug.security import generate_password_hash

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

def test_register(client):
    response = client.post('/register', data=json.dumps({'username': 'testuser', 'password': 'testpass'}), content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'registered successfully'

def test_login(client):
    password_hash = generate_password_hash('testpass', method='pbkdf2')
    user = User(username='testuser', password_hash=password_hash)
    with app.app_context():
        db.session.add(user)
        db.session.commit()
    response = client.post('/login', data=json.dumps({'username': 'testuser', 'password': 'testpass'}), content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'token' in data
