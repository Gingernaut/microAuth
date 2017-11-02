#!/bin/bash
echo " "
echo "----------------------------------------------"
echo "Running dockerstart.sh..."
echo "----------------------------------------------"
echo " "

mkdir logs
touch ./logs/gunicorn.log
touch ./logs/gunicorn-access.log

flask db init
flask db migrate
flask db upgrade

tail -n 0 -f ./logs/gunicorn*.log &

exec gunicorn main:app \
    --bind 0.0.0.0:5000 \
    --workers 4 \
    --log-level=info \
    --log-file=./logs/gunicorn.log \
    --access-logfile=./logs/gunicorn-access.log
    