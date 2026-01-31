#!/bin/sh
set -e

echo "Waiting for database..."
sleep 5

echo "Running migrations..."
python credit_system/manage.py migrate

echo "Ingesting data..."
python credit_system/manage.py ingest_data

echo "Starting server..."
python credit_system/manage.py runserver 0.0.0.0:8000
