FROM python:3.6.1-onbuild
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["/bin/sh", "/app/dockerstart.sh"]