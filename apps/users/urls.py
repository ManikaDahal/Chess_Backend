from django.urls import path
from .views import profile, list_users

urlpatterns = [
    path('profile/', profile, name='profile'),
    path('users/', list_users, name='list_users'),
]
