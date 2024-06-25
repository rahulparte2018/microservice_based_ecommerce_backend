# Microservice Based E-commerce Backend

Developed backend for an e-commerce app with Flask APIs, JWT for authentication, Postgres & SQLAlchemy for the database, Docker & Kubernetes for microservices, Minikube for local deployment, Postman for API testing, Flask-Rate Limiter for API rate limiting, and Redis for caching.

## Setup

Before running the main steps kindly follow this setup

### Step 1: Run a Postgres Database on Docker

1. Pull the Postgres image:

    ```sh
    docker pull postgres
    ```

2. Run the Postgres container:

    ```sh
    docker run \
        --name postgres-db \
        -e POSTGRES_USER=root \
        -e POSTGRES_PASSWORD=root \
        -e POSTGRES_DB=user_db \
        -p 5432:5432 \
        -v pgdata:/var/lib/postgresql/data \
        -d postgres:latest
    ```

### Step 2: Create Additional Databases

1. Connect to the Postgres database:

    ```sh
    psql -d postgres
    ```

2. Create the `product_db` and `order_db` databases:

    ```sql
    CREATE DATABASE product_db;
    CREATE DATABASE order_db;
    ```

### Step 3: Run Redis Server on Docker

1. Pull the Redis image:

    ```sh
    docker pull redis
    ```

2. Run the Redis container:

    ```sh
    docker run --name redis-server -p 6379:6379 -d redis
    ```

## Main Steps

### Step 1: Clone the Git Repository

```sh
git clone https://github.com/rahulparte2018/microservice_based_ecommerce_backend.git
```

### Step 2: Create a Virtual Environment and Install Dependencies for local testing

1. Create a virtual environment:

    ```sh
    python -m venv venv
    ```

2. Install the required dependencies:

    ```sh
    pip install requirements.txt
    ```

3. Add the current directory as the python path

    ```sh
    $env:Path = "current_path_of_project" + $env:Path
    ```

### Step 3: Build Docker Images for Each Microservice

1. Start Docker Desktop or Docker Engine.
2. Build the Docker images (you need a Docker Hub account):

    ```sh
    docker build -t {docker_hub_user_id}/user-auth-service:latest -f user_auth_service/Dockerfile .
    docker build -t {docker_hub_user_id}/product-management-service:latest -f product_management_service/Dockerfile .
    docker build -t {docker_hub_user_id}/order-processing-service:latest -f order_processing_service/Dockerfile .
    ```

### Step 4: Push the Images to Docker Hub Registry

```sh
docker push {docker_hub_user_id}/user-auth-service:latest
docker push {docker_hub_user_id}/product-management-service:latest
docker push {docker_hub_user_id}/order-processing-service:latest
```

### Step 5: Start Minikube and Open the Dashboard

1. Start Minikube:

    ```sh
    minikube start
    ```

2. Open the Minikube dashboard

    ```sh
    minikube dashboard
    ```

### Step 6: Deploy the Microservices on Minikube

```sh
kubectl apply -f user_auth_service/deployment.yaml
kubectl apply -f product_management_service/deployment.yaml
kubectl apply -f order_processing_service/deployment.yaml
```

### Step 7: Get the API Address for Each Microservice

```sh
minikube service user-auth-service
minikube service product-management-service
minikube service order-processing-service
```

### Step 8: Test APIs with Postman

Use Postman to interact and test these APIs. You can use the provided Postman collection to save time:
    <https://elements.getpostman.com/redirect?entityId=27337664-079a63d3-2018-43b3-8c38-f733f3d9503f&entityType=collection>

### Step 9: Delete the Deployment

```sh
kubectl delete -f user_auth_service/deployment.yaml
kubectl delete -f product_management_service/deployment.yaml
kubectl delete -f order_processing_service/deployment.yaml
```

### Step 10: Stop Minikube

```sh
minikube stop
```

## API Documentation

## User Authentication Service

**Base URL:** /

| Endpoint   | Method | Description            | Request Body                                    | Response                                   |
|------------|--------|------------------------|-------------------------------------------------|--------------------------------------------|
| /          | GET    | Base link              | None                                            | `{"message": "flask app user-auth-service"}`     |
| /register  | POST   | Register a new user    | `{"username": "testuser", "password": "testpass"}` | `{"message": "registered successfully"}`      |
| /login     | POST   | Login an existing user | `{"username": "testuser", "password": "testpass"}` | `{"token": "<JWT_TOKEN>"}`                    |

## Product Management Service

**Base URL:** /

| Endpoint   | Method | Description        | Request Body                                                                                     | Response                                   |
|------------|--------|--------------------|--------------------------------------------------------------------------------------------------|--------------------------------------------|
| /          | GET    | Base link          | None                                                 | `{"message": "flask app product-management-service"}`|
| /products  | GET    | Get all products   | None                                                 | `[{"id": 1, "name": "Product1", ...}, ...]`|
| /products  | POST   | Create new product | `{"name": "New Product", "description": "ABC", "price": 100.0, "stock": 50}`  | `{"message": "new product is added to product list"}`|
| /<id>      | PUT    | Update a product   | `{"name": "Updated Product", "description": "Updated", "price": 15.0, "stock": 50, "version": 1}` | `{"message": "product updated successfully"}`|

## Order Processing Service

**Base URL:** /

| Endpoint   | Method | Description         | Request Body                                    | Response                                   |
|------------|--------|---------------------|-------------------------------------------------|--------------------------------------------|
| /          | GET    | Base link           | None                                            | `{"message": "flask app order-processing-service"}`|
| /orders    | GET    | Get all orders      | None                                            | `[{"id": 1, "user_id": 1, ...}, ...]`|
| /orders    | POST   | Create a new order  | `{"user_id": 1, "product_id": 1, "quantity": 10, "version": 1}` | `{"message": "order created successfully"}`|
