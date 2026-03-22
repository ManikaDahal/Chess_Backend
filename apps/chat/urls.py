from django.urls import path
from . import views

urlpatterns = [
    path('history/<int:room_id>/', views.chat_history, name='chat_history'),
    path('get_or_create_room/', views.get_or_create_private_room, name='get_or_create_private_room'),
]
