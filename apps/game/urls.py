from django.urls import path

from . import views

urlpatterns = [
    path('invite/send/', views.send_invite, name='send_invite'),
    path('invite/accept/', views.accept_invite, name='accept_invite'),
    path('invite/decline/', views.decline_invite, name='decline_invite'),
    path('invite/pending/', views.pending_invites, name='pending_invites'),
    
    # Legacy flat paths (WebSocket Project Compatibility)
    path('send-invite/', views.send_invite),
    path('accept-invite/', views.accept_invite),
    path('decline-invite/', views.decline_invite),
    path('pending-invites/', views.pending_invites),
]
