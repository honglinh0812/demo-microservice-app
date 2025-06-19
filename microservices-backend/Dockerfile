FROM python:3.9-slim-buster

WORKDIR /app

COPY microservices-backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY microservices-backend/src /app/src

ENV FLASK_APP=src/main.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5001

EXPOSE 5001

CMD ["flask", "run"]