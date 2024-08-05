#!/bin/sh

# Apply database migrations
# echo "Applying database migrations..."
# python manage.py migrate

# Collect static files
# echo "Collecting static files..."
# python manage.py collectstatic --noinput

# Start Gunicorn
echo "Starting Gevent WSGI Server..."
python pywsgi.py
