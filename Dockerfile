FROM python:3.5
# FROM tbeadle/gunicorn-nginx:3.6-r1-onbuild
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt 
EXPOSE 5000
# --no-cache-dir
ENTRYPOINT ["python3"]
CMD ["main.py"]