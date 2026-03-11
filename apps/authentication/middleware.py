import logging
import time

logger = logging.getLogger('security')

class SecurityLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time

        # Log suspicious activity: high frequency of errors or specific status codes
        if response.status_code in [401, 403, 429]:
            logger.warning(
                f"Security alert: {ip} {request.method} {request.path} -> {response.status_code} "
                f"({duration:.2f}s)"
            )
        elif response.status_code >= 500:
            logger.error(
                f"Server error alert: {ip} {request.method} {request.path} -> {response.status_code} "
                f"({duration:.2f}s)"
            )

        return response
