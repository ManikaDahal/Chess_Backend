from django.urls import path
from . import views
from .views import profile,signup
from .views import forgot_password,verify_otp,reset_password

urlpatterns=[
    path('profile/',profile),
    path('signup/',signup),
    path('forgot-password/',forgot_password),
    path('reset-password/',reset_password),
    path('verify-otp/',verify_otp),

  
   
    
]
