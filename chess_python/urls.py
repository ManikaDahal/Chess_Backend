from django.urls import path
from . import views
from .views import profile,signup

urlpatterns=[
    path('profile/',profile),
    path('signup/',signup),

  
   
    
]
