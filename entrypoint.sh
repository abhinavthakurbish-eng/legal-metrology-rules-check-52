#!/bin/sh
set -e

# Default to Render standard port 10000 or fallback to 5000
PORT="${PORT:-10000}"
echo "=========================================================="
echo "LEGAL METROLOGY COMPLIANCE STUDIO - STARTING UP"
echo "Binding to 0.0.0.0:$PORT"
echo "=========================================================="

mkdir -p /app/uploads /app/generated_reports /app/static/annotated /app/static/samples /app/database

# Start Gunicorn with high-performance worker configuration
exec gunicorn --bind "0.0.0.0:$PORT" --workers 2 --threads 4 --timeout 120 --access-logfile - --error-logfile - app:app
