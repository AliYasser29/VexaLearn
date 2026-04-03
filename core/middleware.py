from django.utils.cache import patch_cache_control

class MediaCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Check if the request is for a media file
        if request.path.startswith('/media/'):
            # Set Cache-Control header for media files (e.g., 1 year)
            patch_cache_control(response, max_age=31536000, public=True)
            
        return response
