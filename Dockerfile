##############################################
FROM alpine:3.13.1 as project-base
WORKDIR /app

ENV VIRTUAL_ENV=/opt/venv

RUN apk add --no-cache \
    python3-dev py3-virtualenv postgresql-dev \
    && python3 -m ensurepip --upgrade \
    && rm -r /usr/lib/python*/ensurepip \
    && pip3 install --upgrade pip setuptools \
    && if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi \
    && if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi \
    && python3 -m virtualenv --python /usr/bin/python3 $VIRTUAL_ENV 

ENV PATH="$VIRTUAL_ENV/bin:$PATH"
##############################################
FROM project-base as dependency-creator

RUN apk add --no-cache build-base libffi-dev \
    && pip3 install --no-cache-dir poetry

COPY poetry.lock pyproject.toml ./
RUN poetry export -f requirements.txt > /requirements.txt && pip3 install -r /requirements.txt

##############################################
FROM project-base as prod-container

RUN apk add --no-cache bash supervisor jq
COPY --from=dependency-creator /opt/venv /opt/venv

COPY supervisord.conf /etc/supervisord.conf
COPY email-templates/ /app/email-templates
COPY gunicorn.conf /app
COPY .env /app
COPY app /app

ENTRYPOINT ["supervisord", "-c", "/etc/supervisord.conf"]
