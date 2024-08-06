#!/bin/sh

# Apply database migrations
# echo "Applying database migrations..."
# python manage.py migrate

# Collect static files
# echo "Collecting static files..."
# python manage.py collectstatic --noinput

# Start server based on the USE_GUNICORN environment variable
if [ "$USE_GUNICORN" = "true" ]; then
    echo "Starting Gunicorn..."
    gunicorn -w 4 -k gevent -b 0.0.0.0:8084 main:app
else
    echo "Starting Gevent WSGI Server..."
    python pywsgi.py
fi