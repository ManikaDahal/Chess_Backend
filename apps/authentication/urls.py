from django.urls import path
from .views import forgot_password, verify_otp
from . import views

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('captcha/', views.GetCaptchaView.as_view(), name='get_captcha'),
    path('axes-status/', views.axes_status, name='axes_status'),
]
