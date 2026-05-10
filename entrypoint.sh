#!/bin/bash
set -e

echo "Waiting for MySQL to be ready..."
while ! python -c "
import os, pymysql
pymysql.connect(
    host=os.environ.get('DB_HOST', 'db'),
    port=int(os.environ.get('DB_PORT', 3306)),
    user=os.environ.get('DB_USER', 'root'),
    password=os.environ.get('DB_PASSWORD', '123456')
)
" 2>/dev/null; do
    echo "MySQL is not ready yet, retrying in 3s..."
    sleep 3
done
echo "MySQL is ready!"

# Run Django migrations
python manage.py migrate --run-syncdb

echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000
