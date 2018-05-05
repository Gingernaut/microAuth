FROM python:3.6.5 AS base

WORKDIR /app
COPY requirements-app.txt /requirements-app.txt
RUN pip install --no-cache-dir -r /requirements-app.txt

COPY ./app /app
COPY .env /app
COPY gunicorn.conf /app

ENTRYPOINT ["gunicorn", "-c", "gunicorn.conf", "main:app"]
