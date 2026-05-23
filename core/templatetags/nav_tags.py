from django import template
from django.urls import resolve

register = template.Library()

@register.simple_tag(takes_context=True)
def is_active(context, url):
    """
    Returns 'active' if the current request path matches the provided URL.
    """
    request = context.get('request')
    if not request:
        return ""
    
    # Check if the path is exactly the URL or if the URL is not root and path starts with it
    if request.path == url:
        return "active"
    
    # Handle cases where the URL might be a parent or subpath
    if url != '/' and request.path.startswith(url):
        return "active"
        
    return ""
