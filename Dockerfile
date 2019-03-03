FROM alpine:3.9
WORKDIR /app

COPY requirements-app.txt /requirements.txt

RUN apk add --no-cache \
    python3-dev build-base postgresql-dev libffi-dev supervisor \
    && python3 -m ensurepip --upgrade \
    && rm -r /usr/lib/python*/ensurepip \
    && pip3 install --upgrade pip setuptools \
    && if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi \
    && if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi \
    && pip3 install --no-cache-dir -r /requirements.txt

COPY supervisord.conf /etc/supervisord.conf
COPY gunicorn.conf /app
COPY .env /app
COPY email-templates /email-templates
COPY app /app

ENTRYPOINT ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
