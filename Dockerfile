FROM python:3.7-rc-stretch

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 5000

CMD ["/bin/sh", "/app/gunicorn.sh"]