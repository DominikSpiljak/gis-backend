FROM python:3.9.10-slim

COPY . /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["python3", "app.py"]
