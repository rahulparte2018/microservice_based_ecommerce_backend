# order_processing_service/app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
from common.jwt_middleware import token_required
import requests
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:root@192.168.29.46:5432/order_db'
app.config['SECRET_KEY'] = 'user_authentication_service'
username = "order_processing_service"
password = "orderprocessingservice"

response_token = requests.post(
        url="http://user-auth-service-clusterip.default.svc.cluster.local:5000/login",
        json={
            'username' : username,
            'password' : password
        }
    )
token = response_token.json()['token']

db = SQLAlchemy(app)
limiter = Limiter(key_func=get_remote_address, app=app)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.UTC))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'status': self.status,
        }
    
    def details(self, product):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product': product,
            'quantity': self.quantity,
            'status': self.status,
        }

with app.app_context():
    # Create the database tables
    db.create_all()

@app.route('/')
@limiter.limit("50 per minute")
def index():
    # response1 = requests.get(
    #     url='http://user-auth-service-clusterip.default.svc.cluster.local:5000'
    # )
    # response2 = requests.get(
    #     url='http://product-management-service-clusterip.default.svc.cluster.local:5001'
    # )
    # response3 = requests.post(
    #     url="http://user-auth-service-clusterip.default.svc.cluster.local:5000/login",
    #     json={
    #         'username' : username,
    #         'password' : password
    #     }
    # )
    return jsonify({
        'message': "flask app order processing service" ,
        # 'response1': response1.json()['message'],
        # 'response2': response2.json()['message'],
        # 'token': token,
        # 'response3': response3.json()
    })
  

@app.route('/orders', methods=['POST'])
@limiter.limit("50 per minute", error_message="rate limited")
@token_required
def create_order(current_user):
    data = request.get_json()
    new_order = Order(user_id=current_user, product_id=data['product_id'], quantity=data['quantity'], status='pending')
    try:
        db.session.add(new_order)
        # url = f"http://172.17.0.5:5001/products/stock/{data['product_id']}"   # this is for docker container
        # url = f"http://127.0.0.1:5001/products/stock/{data['product_id']}"      # this is for local 
        url = f"http://product-management-service-clusterip.default.svc.cluster.local:5001/products/stock/{int(data['product_id'])}"      # this is for local 
        # update the stock quantity of the items
        response = requests.put(
            url=url,
            headers={
                'x-access-token': token
            },
            json={"quantity":data['quantity'], "version":data['version']}
        )
        # print(response)
        if response.status_code != 200:
            raise Exception("Unable to create order. Try again")

        db.session.commit()

        return jsonify({'message': 'order created successfully'})
    
    except Exception as e:
        return jsonify({"message":"Unable to create order. Try again"})


@app.route('/orders', methods=['GET'])
@limiter.limit("50 per minute", error_message="rate limited")
@token_required
def get_orders_for_user(current_user):
    orders = Order.query.filter_by(user_id=current_user).all()
    if len(orders) == 0:
        return jsonify([])
    # get all the products details using product_id in the orders and making request to product management service
    product_ids = [order.product_id for order in orders]
    product_details = requests.post(
        # url="http://172.17.0.5:5001/productsbylist",      # docker
        # url="http://127.0.0.1:5001/productsbylist",         # local hosting
        
        url="http://product-management-service-clusterip.default.svc.cluster.local:5001/productsbylist",         # minikube hosting

        headers={
            'x-access-token': token
        },
        json={'product_list': product_ids}
    )
    product_details = product_details.json()
    print(product_details)
    order_list = []
    for order in orders:
        if str(order.product_id) in product_details.keys():
            order_list.append(order.details(product=product_details[str(order.product_id)]))
    return jsonify(order_list)


if __name__ == '__main__':  
    app.run(debug=True, port=5002)
