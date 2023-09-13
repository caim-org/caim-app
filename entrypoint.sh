#!/usr/bin/env sh

python manage.py migrate
python manage.py collectstatic --no-input
gunicorn --bind :8000 --workers 2 caim.wsgi:application
