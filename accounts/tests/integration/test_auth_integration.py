import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from accounts.models import PasswordResetOTP

User = get_user_model()
