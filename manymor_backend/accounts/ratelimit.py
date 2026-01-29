"""
Rate limiting decorator for API security
"""
from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse
import time


def rate_limit(max_requests=5, window_seconds=60, key_prefix='ratelimit'):
    """
    Rate limit decorator to prevent brute force attacks
    
    Args:
        max_requests: Maximum number of requests allowed
        window_seconds: Time window in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            # Get identifier (IP address or user ID)
            if hasattr(request, 'user') and request.user.is_authenticated:
                identifier = f"user_{request.user.id}"
            else:
                identifier = get_client_ip(request)
            
            # Create cache key
            cache_key = f"{key_prefix}:{identifier}"
            
            # Get current request count
            request_data = cache.get(cache_key, {'count': 0, 'reset_time': time.time() + window_seconds})
            
            # Check if window has expired
            if time.time() > request_data['reset_time']:
                request_data = {'count': 0, 'reset_time': time.time() + window_seconds}
            
            # Increment count
            request_data['count'] += 1
            
            # Check if limit exceeded
            if request_data['count'] > max_requests:
                retry_after = int(request_data['reset_time'] - time.time())
                return JsonResponse(
                    {
                        'error': 'Rate limit exceeded',
                        'detail': f'Too many requests. Please try again in {retry_after} seconds.'
                    },
                    status=429
                )
            
            # Update cache
            cache.set(cache_key, request_data, timeout=window_seconds)
            
            return view_func(request, *args, **kwargs)
        
        return wrapped_view
    return decorator


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
