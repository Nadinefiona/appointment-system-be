#!/usr/bin/env bash
set -o errexit

if [ -z "${DATABASE_URL}" ]; then
  echo "ERROR: DATABASE_URL is not set."
  echo "Render: create PostgreSQL → link DATABASE_URL to this web service → redeploy."
  exit 1
fi

python manage.py migrate --no-input
python manage.py collectstatic --no-input
exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers 2 --timeout 120
