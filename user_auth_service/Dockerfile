# user_auth_service/Dockerfile
# FROM python:3.9.13-slim
FROM python:3.12.4-slim


WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r ./requirements.txt

COPY ./user_auth_service/ .

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]