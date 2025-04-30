#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Starting build process..."

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create staticfiles directory
echo "Creating staticfiles directory..."
mkdir -p staticfiles

# Set permissions for static files
echo "Setting permissions..."
chmod -R 755 staticfiles

# Ensure static directory exists and has correct permissions
echo "Setting up static directory..."
chmod -R 755 static

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Run migrations
echo "Running database migrations..."
python manage.py migrate --no-input

echo "Build process completed!"
