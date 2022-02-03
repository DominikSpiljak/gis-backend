FROM python:3.9.10-slim

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
CMD python3 app.py
