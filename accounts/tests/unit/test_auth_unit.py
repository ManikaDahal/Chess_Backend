import pytest
import random
from django.utils import timezone
from datetime import timedelta
from chess_python.models import PasswordResetOTP
from chess_python.models import FCMToken
from django.contrib.auth import get_user_model

User = get_user_model()


#Password hashing test
@pytest.mark.django_db
def test_password_hashing():
    user = User.objects.create_user(
        username="player1",
        password="Secret123"
    )

    # Password should NOT be stored as plain text
    assert user.password != "Secret123"

    # Django should verify the password correctly
    assert user.check_password("Secret123") is True


#Password reset OTP test
@pytest.mark.django_db
def test_password_reset_otp_created():
    user = User.objects.create_user(username="player2", password="123")

    otp_obj = PasswordResetOTP.objects.create(user=user, otp="123456")

    assert otp_obj.otp == "123456"
    assert otp_obj.user == user


#Duplicate username test
@pytest.mark.django_db
def test_duplicate_username_not_allowed():
    User.objects.create_user(username="player1", password="123")

    with pytest.raises(Exception):
        User.objects.create_user(username="player1", password="456")


#OTP expired test
@pytest.mark.django_db
def test_otp_expired():
    user = User.objects.create_user(username="player3", password="123")

    otp = PasswordResetOTP.objects.create(user=user, otp="654321")
    otp.created_at = timezone.now() - timedelta(minutes=6)
    otp.save()

    assert otp.created_at + timedelta(minutes=5) < timezone.now()


#OTP valid test
@pytest.mark.django_db
def test_otp_valid():
    user = User.objects.create_user(username="player4", password="123")

    otp = PasswordResetOTP.objects.create(user=user, otp="111111")

    assert otp.created_at + timedelta(minutes=5) > timezone.now()


#Password reset logic test
@pytest.mark.django_db
def test_password_reset_logic():
    user = User.objects.create_user(username="player5", password="OldPass123")

    user.set_password("NewPass123")
    user.save()

    assert user.check_password("NewPass123")



#FCM token test
@pytest.mark.django_db
def test_fcm_token_update_or_create():
    user = User.objects.create_user(username="player6", password="123")

    token1, created1 = FCMToken.objects.update_or_create(
        token="abc123",
        defaults={"user": user}
    )

    token2, created2 = FCMToken.objects.update_or_create(
        token="abc123",
        defaults={"user": user}
    )

    assert token1.id == token2.id
    assert created1 is True
    assert created2 is False

