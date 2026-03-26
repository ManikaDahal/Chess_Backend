from django.urls import path
from .views import CreatePaymentIntentView, StripeWebhookView, ConfirmPaymentView

urlpatterns = [
    path('create-payment-intent/', CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('confirm-payment/', ConfirmPaymentView.as_view(), name='confirm-payment'),
]
