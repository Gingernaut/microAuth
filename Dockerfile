##############################################
FROM alpine:3.11.5 as project-base
WORKDIR /app

RUN apk add --no-cache \
    python3-dev build-base postgresql-dev libffi-dev bash supervisor \
    && python3 -m ensurepip --upgrade \
    && rm -r /usr/lib/python*/ensurepip \
    && pip3 install --upgrade pip setuptools \
    && if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi \
    && if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi

##############################################
FROM project-base as dependency-creator

RUN pip3 install --no-cache-dir poetry
COPY poetry.lock pyproject.toml ./
RUN poetry export -f requirements.txt > /requirements.txt

##############################################
FROM project-base as prod-container

COPY --from=dependency-creator /requirements.txt /requirements.txt
# COPY requirements-app.txt /requirements.txt

# RUN apk add --no-cache openssl-dev
RUN pip3 install -r /requirements.txt

COPY supervisord.conf /etc/supervisord.conf
COPY email-templates/ /app/email-templates
COPY gunicorn.conf /app
COPY .env /app
COPY app /app

ENTRYPOINT ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
