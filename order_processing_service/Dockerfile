# product_management_service/Dockerfile
# FROM python:3.9.13-slim
FROM python:3.12.4-slim


WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./order_processing_service ./order_processing_service
COPY ./common/ ./common/

EXPOSE 5002
ENV FLASK_APP=order_processing_service/app.py

CMD ["flask", "run", "--host=0.0.0.0", "--port=5002"]