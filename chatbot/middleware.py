import time
import json
import logging
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings
from .signals import conversation_started, conversation_ended, error_occurred

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware to log all requests and responses"""
    
    def process_request(self, request):
        """Log incoming requests"""
        request.start_time = time.time()
        
        # Log request details
        log_data = {
            'method': request.method,
            'path': request.path,
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'ip_address': self.get_client_ip(request),
            'timestamp': time.time()
        }
        
        logger.info(f"Request: {json.dumps(log_data)}")
        
        # Track API usage
        if request.path.startswith('/api/'):
            api_requests = cache.get('api_requests_count', 0)
            cache.set('api_requests_count', api_requests + 1, 3600)
    
    def process_response(self, request, response):
        """Log response details"""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Log response details
            log_data = {
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration': round(duration, 3),
                'timestamp': time.time()
            }
            
            logger.info(f"Response: {json.dumps(log_data)}")
            
            # Track slow requests
            if duration > 2.0:  # Log requests taking more than 2 seconds
                logger.warning(f"Slow request detected: {request.path} took {duration:.3f}s")
            
            # Add performance header
            response['X-Response-Time'] = f"{duration:.3f}s"
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class ChatAnalyticsMiddleware(MiddlewareMixin):
    """Middleware to track chat-specific analytics"""
    
    def process_request(self, request):
        """Track chat-related requests"""
        if request.path == '/' and request.method == 'POST':
            # Track new conversation starts
            user_message = request.POST.get('message', '')
            if user_message:
                conversation_started.send(
                    sender=self.__class__,
                    user_message=user_message
                )
        
        elif request.path == '/api/chat/' and request.method == 'POST':
            # Track API chat requests
            try:
                body = json.loads(request.body.decode('utf-8'))
                user_message = body.get('message', '')
                if user_message:
                    conversation_started.send(
                        sender=self.__class__,
                        user_message=user_message
                    )
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass

class ErrorHandlingMiddleware(MiddlewareMixin):
    """Middleware to handle and log errors"""
    
    def process_exception(self, request, exception):
        """Handle exceptions and log them"""
        error_data = {
            'error_type': type(exception).__name__,
            'error_message': str(exception),
            'path': request.path,
            'method': request.method,
            'timestamp': time.time()
        }
        
        logger.error(f"Exception occurred: {json.dumps(error_data)}")
        
        # Send error signal
        error_occurred.send(
            sender=self.__class__,
            error_type=type(exception).__name__,
            error_message=str(exception)
        )
        
        # Return JSON error response for API requests
        if request.path.startswith('/api/'):
            return JsonResponse({
                'error': 'Internal server error',
                'error_type': 'server_error'
            }, status=500)
        
        return None

class RateLimitingMiddleware(MiddlewareMixin):
    """Simple rate limiting middleware"""
    
    def process_request(self, request):
        """Check rate limits"""
        if request.path.startswith('/api/'):
            client_ip = self.get_client_ip(request)
            cache_key = f"rate_limit_{client_ip}"
            
            # Get current request count
            request_count = cache.get(cache_key, 0)
            
            # Rate limit: 100 requests per hour
            if request_count >= 100:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                return JsonResponse({
                    'error': 'Rate limit exceeded. Please try again later.',
                    'error_type': 'rate_limit'
                }, status=429)
            
            # Increment request count
            cache.set(cache_key, request_count + 1, 3600)  # 1 hour expiry
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class SecurityHeadersMiddleware(MiddlewareMixin):
    """Middleware to add security headers"""
    
    def process_response(self, request, response):
        """Add security headers to response"""
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' fonts.googleapis.com cdnjs.cloudflare.com; "
            "font-src 'self' fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self';"
        )
        response['Content-Security-Policy'] = csp
        
        return response
