web: cd backend/src && gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
worker: cd backend/src && celery -A celery_app worker --loglevel=info --concurrency=2
