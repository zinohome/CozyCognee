#!/bin/bash

set -e  # Exit on error
echo "Debug mode: $DEBUG"
echo "Environment: $ENVIRONMENT"

# Set default ports if not specified
DEBUG_PORT=${DEBUG_PORT:-5678}
HTTP_PORT=${HTTP_PORT:-8000}
echo "Debug port: $DEBUG_PORT"
echo "HTTP port: $HTTP_PORT"

# Run Alembic migrations with proper error handling.
# Note on UserAlreadyExists error handling:
# During database migrations, we attempt to create a default user. If this user
# already exists (e.g., from a previous deployment or migration), it's not a
# critical error and shouldn't prevent the application from starting. This is
# different from other migration errors which could indicate database schema
# inconsistencies and should cause the startup to fail. This check allows for
# smooth redeployments and container restarts while maintaining data integrity.
echo "Running database migrations..."

MIGRATION_OUTPUT=$(alembic upgrade head)
MIGRATION_EXIT_CODE=$?

if [[ $MIGRATION_EXIT_CODE -ne 0 ]]; then
    if [[ "$MIGRATION_OUTPUT" == *"UserAlreadyExists"* ]] || [[ "$MIGRATION_OUTPUT" == *"User default_user@example.com already exists"* ]]; then
        echo "Warning: Default user already exists, continuing startup..."
    else
        echo "Migration failed with unexpected error."
        exit 1
    fi
fi

echo "Database migrations done."

# Note: pgvector is built into PostgreSQL and doesn't require adapter registration
# If using other vector databases, add registration logic here

echo "Starting server..."

# Add startup delay to ensure DB is ready
sleep 2

# Modified Gunicorn startup with error handling
if [ "$ENVIRONMENT" = "dev" ] || [ "$ENVIRONMENT" = "local" ]; then
    if [ "$DEBUG" = "true" ]; then
        echo "Waiting for the debugger to attach..."
        debugpy --wait-for-client --listen 0.0.0.0:$DEBUG_PORT -m gunicorn -w 1 -k uvicorn.workers.UvicornWorker -t 30000 --bind=0.0.0.0:$HTTP_PORT --log-level debug --reload cognee.api.client:app
    else
        gunicorn -w 1 -k uvicorn.workers.UvicornWorker -t 30000 --bind=0.0.0.0:$HTTP_PORT --log-level debug --reload cognee.api.client:app
    fi
else
    # 生产环境：增加 worker 超时时间，添加 max_requests 防止内存泄漏
    # --max-requests: 每个 worker 处理请求数后重启，防止内存泄漏
    # --max-requests-jitter: 随机化重启，避免所有 worker 同时重启
    # --timeout: 增加超时时间，避免长时间操作导致 worker 被杀死
    gunicorn -w 1 -k uvicorn.workers.UvicornWorker \
        --timeout 300 \
        --graceful-timeout 30 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --bind=0.0.0.0:$HTTP_PORT \
        --log-level error \
        --access-logfile - \
        --error-logfile - \
        cognee.api.client:app
fi

