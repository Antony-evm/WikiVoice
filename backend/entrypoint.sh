#!/bin/sh
set -e

echo "Running Alembic migrations..."
alembic upgrade head
echo "Starting Gunicorn server with Uvicorn workers..."
exec gunicorn main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers ${WORKERS:-1} \
    --bind 0.0.0.0:${PORT:-8000} \
    --max-requests ${MAX_REQUESTS_PER_WORKER:-10000} \
    --max-requests-jitter ${MAX_REQUESTS_JITTER:-1000} \
    --graceful-timeout ${SHUTDOWN_TIMEOUT_SECONDS:-30} \
    --access-logfile - \
    --error-logfile - \
    --log-level info
