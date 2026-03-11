from django.urls import path
from .views import signup, forgot_password, verify_otp, reset_password, EmailTokenObtainPairView

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('reset-password/', reset_password, name='reset_password'),
    path('login/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
]
