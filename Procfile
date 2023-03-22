web: gunicorn nftion.wsgi --log-file -
worker: celery -A nftion worker --concurrency=3 -E -l INFO
beat: celery -A nftion beat -l INFO