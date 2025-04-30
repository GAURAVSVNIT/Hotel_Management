"""
WSGI config for hotel_management project.

It exposes the WSGI callable as a module-level variable named ``application``.

Enhanced with logging for Render deployment diagnostics.
"""

import os
import sys
import logging
from pathlib import Path

from django.core.wsgi import get_wsgi_application

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Log environment information
logger.info("Initializing WSGI application")
logger.info(f"Python version: {sys.version}")
logger.info(f"Current directory: {os.getcwd()}")

# Get the base directory
BASE_DIR = Path(__file__).resolve().parent.parent
logger.info(f"Project base directory: {BASE_DIR}")

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel_management.settings')
logger.info(f"Django settings module: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

try:
    # Log available Python modules in project path
    sys.path.insert(0, str(BASE_DIR))
    logger.info(f"Updated Python path: {sys.path}")
    
    # Initialize WSGI application
    logger.info("Getting WSGI application...")
    application = get_wsgi_application()
    logger.info("WSGI application initialized successfully")
except Exception as e:
    logger.error(f"Error initializing WSGI application: {str(e)}", exc_info=True)
    raise
