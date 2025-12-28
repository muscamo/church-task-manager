#!/bin/bash

# Church Task Manager - Start Script
# Usage: ./start.sh [dev|prod]

MODE=${1:-dev}

echo "Starting Church Task Manager in $MODE mode..."

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Virtual environment activated"
else
    echo "Virtual environment not found. Creating one..."
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Install dependencies
pip install -r requirements.txt

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the server based on mode
if [ "$MODE" = "prod" ]; then
    echo "Starting production server with Gunicorn..."
    gunicorn church_task_manager.wsgi:application --bind 0.0.0.0:8000
else
    echo "Starting development server..."
    python manage.py runserver 0.0.0.0:8000
fi
