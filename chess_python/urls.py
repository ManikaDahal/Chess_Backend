from django.urls import path
from . import views
from .views import profile,signup

urlpatterns=[
    path('api/profile/',profile),
    path('api/signup/',signup),

  
   
    
]
