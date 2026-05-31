#!/usr/bin/env bash
set -o errexit

python manage.py migrate --no-input
python manage.py collectstatic --no-input
exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers 2 --timeout 120
