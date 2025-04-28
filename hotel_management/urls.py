from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.http import FileResponse, HttpResponse
import logging
import os
import mimetypes

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

# Define main URL patterns
urlpatterns = debug_patterns + [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('rating/', include('ratings.urls')),
]

# Add logging middleware to settings
if 'RequestLoggingMiddleware' not in str(settings.MIDDLEWARE):
    settings.MIDDLEWARE.insert(0, 'hotel_management.urls.RequestLoggingMiddleware')

# Add static and media URL patterns for production
if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
