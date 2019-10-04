web: gunicorn backend.wsgi --log-file -
release: python manage.py migrate
worker: celery -A backend worker
beat: celery -A backend beat -S django