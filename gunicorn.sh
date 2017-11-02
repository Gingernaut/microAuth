echo "----------------------------------------------"
echo "Starting Gunicorn"
echo "----------------------------------------------\n"

# cd /app/app
cd ./app

rm -rf ./logs && mkdir logs
touch ./logs/gunicorn.log
touch ./logs/gunicorn-access.log

tail -n 0 -f ./logs/gunicorn*.log &

exec gunicorn main:__hug_wsgi__ \
    --bind 0.0.0.0:5000 
    --workers 4 \
    --log-level=info \
    --log-file=./logs/gunicorn.log \
    --access-logfile=./logs/gunicorn-access.log