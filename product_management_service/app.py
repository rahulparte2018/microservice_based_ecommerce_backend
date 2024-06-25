from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import StaleDataError
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from common.jwt_middleware import token_required
import redis
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:root@192.168.29.46:5432/product_db'
app.config['SECRET_KEY'] = 'user_authentication_service'

db = SQLAlchemy(app)
limiter = Limiter(key_func=get_remote_address, app=app)
# Create a cache store
cache = redis.StrictRedis(host='192.168.29.46', port=6379, db=0)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    version = db.Column(db.Integer, nullable=False, default=1)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'version': self.version,
        }

    def provide_description(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
        }

with app.app_context():
    # Create the database tables
    db.create_all()


@app.route('/')
@limiter.limit("50 per minute")
def index():
    return jsonify({'message':'flask app product management service'})     

@app.route('/products', methods=['GET', 'POST'])
@limiter.limit("50 per minute")
@token_required
def handle_products(current_user):
    if request.method == 'GET':
        # search the cache store for cache value
        cached_products = cache.get('products')
        if cached_products:
            return jsonify(json.loads(cached_products))
        products = Product.query.all()
        products_list = [product.to_dict() for product in products]
        # add the cache value in the cache store
        cache.set('products', json.dumps(products_list), ex=300)  # cache for 5 minutes
        return jsonify(products_list)
    else:
        data = request.json
        new_product = Product(name=data['name'],description=data['description'],price=data['price'],stock=data['stock'],version=1)
        db.session.add(new_product)
        db.session.commit()
        cache.delete('products')
        return f"{data['name']} is added to the product list"

@app.route('/products/<id>', methods=['PUT'])
@limiter.limit("25 per minute")
@token_required
def update_product(current_user, id):
    data = request.get_json()
    product = Product.query.filter_by(id=id).first()
    if product.version != data['version']:
        return jsonify({'message': 'version conflict'}), 409
    try:
        product.name = data['name']
        product.description = data['description']
        product.price = data['price']
        product.stock = data['stock']
        product.version += 1
        db.session.commit()
        # delete the cache when a new product is updated only
        cache.delete('products')
    except StaleDataError:
        db.session.rollback()
        return jsonify({'message': 'version conflict'}), 409
    return jsonify({'message': 'product updated successfully'})

@app.route('/products/stock/<id>', methods=['PUT'])
@limiter.limit("25 per minute")
@token_required
def update_stock(current_user, id):
    data = request.get_json()
    product = Product.query.filter_by(id=id).first()
    if product.version != data['version']:
        return jsonify({'message': 'version conflict'}), 409
    print(data['quantity'], product.stock)
    if data['quantity'] > product.stock:
        return jsonify({'message':"Out of Stock"}), 400
    try:
        product.stock -= data['quantity']
        product.version += 1
        db.session.commit()
        # delete the cache when a new product is updated only
        cache.delete('products')
    except StaleDataError:
        db.session.rollback()
        return jsonify({'message': 'version conflict'}), 409
    return jsonify({'message': 'product updated successfully'})

@app.route('/productsbylist', methods=['POST'])
@limiter.limit("50 per minute")
@token_required
def get_products_using_product_id(current_user):
    data = request.get_json()
    if len(data['product_list']) == 0:
        return jsonify({})
    products = Product.query.filter(Product.id.in_(data['product_list'])).all()
    product_dict = dict()
    for product in products:
        product_dict[product.id] = product.provide_description()
    # return jsonify([product.provide_description() for product in products])
    return jsonify(product_dict)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
