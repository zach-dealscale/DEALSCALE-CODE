#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Wait for the database to be ready
echo "Waiting for database..."

echo "Database is ready."

# Run database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files in production

# Execute the CMD provided in the Dockerfile or docker-compose
exec "$@"
