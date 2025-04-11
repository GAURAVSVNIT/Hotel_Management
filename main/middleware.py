import os
import mimetypes
import logging
import asyncio
from contextlib import contextmanager
from django.conf import settings
from django.http import HttpResponse, FileResponse
from django.utils.decorators import sync_and_async_middleware

logger = logging.getLogger(__name__)

@sync_and_async_middleware
class MediaFilesMiddleware:
    """
    Middleware to handle media files with proper cache control and content type headers.
    This helps ensure media files are properly served and cached by browsers.
    
    Supports both sync and async operations using Django's sync_and_async_middleware.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Initialize MIME types
        mimetypes.init()
        logger.info("MediaFilesMiddleware initialized")
    
    def __call__(self, request):
        """Synchronous request handler"""
        # Check if this is a media file request
        if request.path.startswith(settings.MEDIA_URL):
            response = self.handle_media_request(request)
            if response:
                return response
        
        # Not a media file or file not found, continue with regular processing
        return self.get_response(request)
    
    async def __acall__(self, request):
        """Asynchronous request handler"""
        # Check if this is a media file request
        if request.path.startswith(settings.MEDIA_URL):
            # Use sync_to_async to handle file operations which are blocking
            response = await asyncio.to_thread(self.handle_media_request, request)
            if response:
                return response
        
        # Not a media file or file not found, continue with regular processing
        return await self.get_response(request)
    
    def handle_media_request(self, request):
        """Handle media file requests for both sync and async contexts"""
        # Extract relative path from media URL
        relative_path = request.path[len(settings.MEDIA_URL):]
        # Construct absolute file path
        file_path = os.path.join(settings.MEDIA_ROOT, relative_path)
        
        # Check if file exists
        if os.path.exists(file_path) and os.path.isfile(file_path):
            try:
                # Get content type based on file extension
                content_type, encoding = mimetypes.guess_type(file_path)
                if not content_type:
                    content_type = 'application/octet-stream'
                
                # Use FileResponse for better performance with proper file handling
                with open(file_path, 'rb') as f:
                    response = FileResponse(f, content_type=content_type)
                    
                    # Set cache control headers
                    response['Cache-Control'] = 'public, max-age=31536000'  # Cache for 1 year
                    response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                    response['Accept-Ranges'] = 'bytes'  # Support range requests for video/audio
                    
                    logger.info(f"Serving media file: {file_path}")
                    return response
            except FileNotFoundError:
                logger.error(f"Media file not found: {file_path}")
            except PermissionError:
                logger.error(f"Permission denied for media file: {file_path}")
            except Exception as e:
                logger.error(f"Error serving media file {file_path}: {str(e)}")
        
        # File doesn't exist or error occurred
        return None

