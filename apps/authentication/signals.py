from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
import logging

logger = logging.getLogger('security')

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    username = credentials.get('username') or credentials.get('email') or 'unknown'
    ip = request.META.get('REMOTE_ADDR') if request else 'unknown'
    logger.warning(f"DIAGNOSTIC: Login failed for user '{username}' from IP '{ip}'")
    
    # We can also manually trigger axes if needed here, 
    # but let's see if this signal even fires first.
