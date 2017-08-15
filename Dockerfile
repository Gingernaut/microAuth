FROM python:3.6-onbuild
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt 
EXPOSE 5000
CMD ["/bin/sh", "/app/dockerstart.sh"]