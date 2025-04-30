from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.http import FileResponse, HttpResponse, JsonResponse
import logging
import os
import mimetypes
import sys
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Request logging middleware
class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info(f"Received request: {request.method} {request.path}")
        response = self.get_response(request)
        logger.info(f"Response status: {response.status_code}")
        return response

# Custom media file handler with logging
def logged_media_serve(request, path, document_root, show_indexes):
    logger.info(f"Media request: {path}")
    logger.info(f"Looking in: {document_root}/{path}")
    try:
        response = serve(request, path, document_root, show_indexes)
        logger.info(f"Media served successfully: {path}")
        return response
    except Exception as e:
        logger.error(f"Error serving media: {path}, Error: {str(e)}")
        raise

# Test view for a specific image
def test_image_view(request):
    image_path = os.path.join(settings.MEDIA_ROOT, 'restaurants', 'Korean_Res.png')
    logger.info(f"Test image path: {image_path}")
    
    if os.path.exists(image_path):
        logger.info(f"Test image exists: {image_path}")
        content_type, encoding = mimetypes.guess_type(image_path)
        if not content_type:
            content_type = 'application/octet-stream'
        
        # Open the file but let FileResponse manage the file handle
        # Don't use 'with' statement as it will close the file
        # FileResponse will close the file automatically
        image_file = open(image_path, 'rb')
        response = FileResponse(image_file, content_type=content_type)
        response['Content-Disposition'] = f'inline; filename=test_image.png'
        return response
    else:
        logger.error(f"Test image not found: {image_path}")
        return HttpResponse(f"Image not found at {image_path}", status=404)

# Define debug patterns for development
debug_patterns = []
if settings.DEBUG:
    # Print debug information
    logger.info(f"Media URL: {settings.MEDIA_URL}")
    logger.info(f"Media Root: {settings.MEDIA_ROOT}")
    logger.info(f"Static URL: {settings.STATIC_URL}")
    logger.info(f"Static Root: {settings.STATIC_ROOT}")
    
    # Media files handler with explicit path
    debug_patterns = [
        # Explicitly serve media files with logging
        re_path(r'^media/(?P<path>.*)$', 
                lambda request, path: logged_media_serve(
                    request, path, document_root=settings.MEDIA_ROOT, show_indexes=True
                ),
                name='media'
        ),
        # Explicitly serve static files
        re_path(r'^static/(?P<path>.*)$', serve, {
            'document_root': settings.STATIC_ROOT,
            'show_indexes': True,
        }, name='static'),
        
        # Direct test patterns for specific files
        path('test-image/', test_image_view, name='test_image'),
        
        # Test pattern for a specific media file
        path('korean-restaurant-image/', 
             lambda request: serve(request, 'restaurants/Korean_Res.png', document_root=settings.MEDIA_ROOT),
             name='korean_image'),
    ]  
# Enhanced health check endpoint for Render deployment verification
def health_check(request):
    """
    Enhanced health check endpoint that returns application status
    and environment information as JSON. Optimized for Render deployment.
    """
    logger.info("Health check requested")
    
    try:
        # Check for critical directories
        media_exists = os.path.exists(settings.MEDIA_ROOT)
        static_exists = os.path.exists(settings.STATIC_ROOT)
        media_items_exists = os.path.exists(os.path.join(settings.MEDIA_ROOT, 'menu_items'))
        restaurants_exists = os.path.exists(os.path.join(settings.MEDIA_ROOT, 'restaurants'))
        
        # Count files in directories
        media_files_count = sum(len(files) for _, _, files in os.walk(settings.MEDIA_ROOT)) if media_exists else 0
        static_files_count = sum(len(files) for _, _, files in os.walk(settings.STATIC_ROOT)) if static_exists else 0
        
        # Check mountpoint if on Render
        render_disk_mounted = False
        render_mountpath = '/opt/render/project/src/media'
        if os.environ.get('RENDER') == 'true':
            render_disk_mounted = os.path.exists(render_mountpath) and os.path.ismount(render_mountpath)
            logger.info(f"Render disk mount check: {render_disk_mounted}")
        
        # Get a list of sample files to verify
        sample_files = []
        if media_items_exists:
            try:
                sample_files = os.listdir(os.path.join(settings.MEDIA_ROOT, 'menu_items'))[:5]
            except Exception as e:
                logger.error(f"Error listing menu items: {str(e)}")
        
        # Build status response
        status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'render': {
                'is_render': os.environ.get('RENDER') == 'true',
                'disk_mounted': render_disk_mounted,
                'external_url': os.environ.get('RENDER_EXTERNAL_URL', 'not set'),
            },
            'environment': os.environ.get('DJANGO_ENV', 'not set'),
            'python_version': sys.version,
            'debug_mode': settings.DEBUG,
            'allowed_hosts': settings.ALLOWED_HOSTS,
            'csrf_trusted_origins': settings.CSRF_TRUSTED_ORIGINS,
            'directories': {
                'media_root': {
                    'path': settings.MEDIA_ROOT,
                    'exists': media_exists,
                    'files_count': media_files_count,
                    'is_writable': os.access(settings.MEDIA_ROOT, os.W_OK) if media_exists else False,
                },
                'static_root': {
                    'path': settings.STATIC_ROOT,
                    'exists': static_exists,
                    'files_count': static_files_count,
                    'is_writable': os.access(settings.STATIC_ROOT, os.W_OK) if static_exists else False,
                },
                'menu_items': {
                    'path': os.path.join(settings.MEDIA_ROOT, 'menu_items'),
                    'exists': media_items_exists,
                    'sample_files': sample_files[:5] if sample_files else []
                },
                'restaurants': {
                    'path': os.path.join(settings.MEDIA_ROOT, 'restaurants'),
                    'exists': restaurants_exists
                }
            }
        }
        
        logger.info(f"Health check response: {status}")
        return JsonResponse(status)
    except Exception as e:
        logger.error(f"Health check failed with error: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=500)
    logger.info(f"Health check response: {status}")
    return JsonResponse(status)

# Define main URL patterns
urlpatterns = debug_patterns + [
# Health check should be accessible without authentication
path('health/', health_check, name='health_check'),
path('admin/', admin.site.urls),
path('', include('main.urls')),
#path('rating/', include('ratings.urls')),
]

# Add logging middleware to settings
if 'RequestLoggingMiddleware' not in str(settings.MIDDLEWARE):
    settings.MIDDLEWARE.insert(0, 'hotel_management.urls.RequestLoggingMiddleware')

# Add static and media URL patterns for both development and production
# In production, WhiteNoise will handle static files
# For media files, we'll let Django handle them directly for now
# A more robust solution would be to use S3 or similar cloud storage

# For static files:
# - In development, Django will serve them directly
# - In production, WhiteNoise will serve them from the STATIC_ROOT directory
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# For media files: Django will serve them both in development and production
# This is fine for smaller applications, but for production-scale apps,
# consider using cloud storage like AWS S3 or similar
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Log configuration information
logger.info(f"Static URL: {settings.STATIC_URL}, Root: {settings.STATIC_ROOT}")
logger.info(f"Media URL: {settings.MEDIA_URL}, Root: {settings.MEDIA_ROOT}")
logger.info(f"Debug mode: {settings.DEBUG}")
logger.info(f"Environment: {getattr(settings, 'DJANGO_ENV', 'not set')}")
