# user_authentication_service/app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import jwt.utils
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import jwt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://root:root@192.168.29.46:5432/user_db"
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://root:root@localhost:5432/userdb"
app.config['SECRET_KEY'] = "user_authentication_service"

db = SQLAlchemy(app)
limiter = Limiter(key_func=get_remote_address, app=app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default= datetime.datetime.now(datetime.UTC))

with app.app_context():
    # Create the database tables
    db.create_all()

@app.route('/')
@limiter.limit("5 per minute")
def index():
    return jsonify({'message':'flask app user authentication service'})

@app.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='pbkdf2')
    try:
        new_user = User(username=data['username'], password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'registered successfully'})
    except IntegrityError as e:
        db.session.rollback()  # Roll back the session to the previous state
        if "duplicate key" in str(e.orig):
            return jsonify({'message': 'user already registered. kindly go login'}), 409
        else:
            raise

@app.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'message': 'login failed'}), 401
    token = jwt.api_jwt.encode({'user_id': user.id, 'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=24)}, app.config['SECRET_KEY'])
    return jsonify({'token': token}), 200

if __name__ == '__main__':
    app.run(debug=True)