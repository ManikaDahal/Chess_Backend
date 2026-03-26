from django.db import models
from django.conf import settings

class PaymentIntentRecord(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    intent_id = models.CharField(max_length=255, unique=True)
    amount = models.IntegerField()  # Amount in cents
    currency = models.CharField(max_length=10, default='usd')
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    coins_awarded = models.IntegerField(default=0)

    class Meta:
        db_table = 'payments_paymentintentrecord'

    def __str__(self):
        return f"{self.user.username} - {self.intent_id} ({self.status})"
