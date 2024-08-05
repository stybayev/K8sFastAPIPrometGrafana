#!/bin/sh

# Apply database migrations
# echo "Applying database migrations..."
# python manage.py migrate

# Collect static files
# echo "Collecting static files..."
# python manage.py collectstatic --noinput

# Start Gunicorn
echo "Starting Gunicorn..."
gunicorn -w 4 -k gevent -b 0.0.0.0:8083 main:app

