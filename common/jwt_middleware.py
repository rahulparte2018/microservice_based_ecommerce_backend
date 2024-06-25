# common/jwt_middleware.py
from functools import wraps
from flask import request, jsonify
from jwt.api_jwt import decode

SECRET_KEY = 'user_authentication_service'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = data['user_id']
        except Exception as e:
            return jsonify({'message': f'Token is invalid: {e}'}), 401
        return f(current_user, *args, **kwargs)
    return decorated
