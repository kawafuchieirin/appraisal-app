"""
Custom middleware for handling health checks and security
"""
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse

class HealthCheckMiddleware(MiddlewareMixin):
    """
    Middleware to handle ALB health checks without CSRF validation
    """
    def process_request(self, request):
        # Skip CSRF for health check user agents
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if 'ELB-HealthChecker' in user_agent:
            request._dont_enforce_csrf_checks = True
        
        # Handle health check at root path for ALB
        if request.path == '/' and 'ELB-HealthChecker' in user_agent:
            return HttpResponse('OK', content_type='text/plain')
        
        return None