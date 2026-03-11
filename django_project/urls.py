"""
URL configuration for django_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path,include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import HttpResponse

def home(request):
    return HttpResponse("Chess Backend is running successfully ")

from apps.authentication.views import EmailTokenObtainPairView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

schema_view=get_schema_view(
    openapi.Info(
        title="Authentication API",
        default_version='v1',
        description="Login, Register, Forgot Password, Verify OTP, Reset Password APIs",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    authentication_classes=[],


)

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    
    # FEATURE APPS (Legacy Compatible)
    path('api/', include('apps.authentication.urls')),
    path('api/', include('apps.users.urls')),
    path('api/', include('apps.notifications.urls')),
    path('api/', include('apps.game.urls')),
    path('captcha/', include('captcha.urls')),
    
    path('api/token/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # SWAGGER documentation URLs
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/schema/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

