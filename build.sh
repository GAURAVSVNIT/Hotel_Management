#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Starting build process..."

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p media/menu_items
mkdir -p media/restaurants
mkdir -p staticfiles

# Set permissions
echo "Setting permissions..."
chmod -R 755 media
chmod -R 755 staticfiles

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Run migrations
echo "Running database migrations..."
python manage.py migrate --no-input

echo "Build process completed!"
