# product_management_service/Dockerfile
# FROM python:3.9.13-slim
FROM python:3.12.4-slim


WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./product_management_service/ ./product_management_service
COPY ./common/ ./common/

EXPOSE 5001
ENV FLASK_APP=product_management_service/app.py

# CMD ["flask", "run", "--host=0.0.0.0", "--port=5001",  "--app", "product_management_service/app.py"]
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]
