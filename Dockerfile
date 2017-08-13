FROM python:3.5
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt 
EXPOSE 5000
# --no-cache-dir
ENTRYPOINT ["python3"]
CMD ["main.py"]