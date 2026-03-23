from django.urls import path
from . import views, video_views, voice_views

urlpatterns = [
    path('call/upload/', views.upload_recording, name='recording-upload'),
    
    # Video API endpoints
    path('videos/', video_views.list_videos, name='list_videos'),
    path('videos/<int:video_id>/', video_views.get_video_detail, name='video_detail'),
    path('videos/<int:video_id>/stream/', video_views.stream_video, name='stream_video'),
    path('videos/upload/', video_views.upload_video, name='upload_video'),
    path('videos/<int:video_id>/delete/', video_views.delete_video, name='delete_video'),
    path('videos/<int:video_id>/comments/', video_views.video_comments, name='video_comments'),
    path('videos/<int:video_id>/react/', video_views.toggle_reaction, name='toggle_reaction'),
    
    # AI Voice Cloning Endpoints
    path('voice/upload-samples/', voice_views.upload_voice_samples, name='upload_voice_samples'),
    path('voice/chat-self/', voice_views.chat_with_self, name='chat_with_self'),
    path('voice/status/', voice_views.get_voice_status, name='get_voice_status'),
    path('voice/delete-profile/', voice_views.delete_voice_profile, name='delete_voice_profile'),
]
