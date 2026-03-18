from django.urls import path
from .views import profile, list_users, update_coins, claim_daily_gift

urlpatterns = [
    path('profile/', profile, name='profile'),
    path('users/', list_users, name='list_users'),
    path('update-coins/', update_coins, name='update_coins'),
    path('claim-daily-gift/', claim_daily_gift, name='claim_daily_gift'),
]
