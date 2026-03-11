from django.db import models
from django.conf import settings

class FCMToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fcm_tokens')
    token = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chess_python_fcmtoken' # Keep original table name

    def __str__(self):
        return f"{self.user.username} - {self.token[:10]}..."
