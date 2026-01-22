from django.contrib import admin
from .models import CustomUser, PasswordResetOTP

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'phone', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'phone')

@admin.register(PasswordResetOTP)
class PasswordResetOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp', 'created_at')
