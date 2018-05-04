FROM python:3.6.5 AS base

WORKDIR /app
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

COPY ./app /app
COPY .env /app
COPY gunicorn.conf /app

ENTRYPOINT ["gunicorn", "-c", "gunicorn.conf", "main:app"]
