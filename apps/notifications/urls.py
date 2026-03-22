from django.urls import path
from .views import (
    register_fcm_token,
    update_notification_status,
    get_notification_preferences,
    update_notification_preference
)

urlpatterns = [
    path('register-fcm-token/', register_fcm_token, name='register_fcm_token'),
    
    # WebSocket Project / Render Backend Compatibility
    path('notifications/update-status/', update_notification_status, name='update_notification_status'),
    path('notifications/preferences/', get_notification_preferences, name='get_notification_preferences'),
    path('notifications/preferences/update/', update_notification_preference, name='update_notification_preference'),
]
