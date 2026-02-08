import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from chess_python.models import PasswordResetOTP, FCMToken

User = get_user_model()

#Signup test
@pytest.mark.django_db
def test_signup_success():
    client = APIClient()

    response = client.post(
        "/api/signup/",
        {
            "username": "player1",
            "email": "player1@test.com",
            "password": "Secret123"
        },
        format="json"
    )

    assert response.status_code == 201
    assert "access" in response.data
    assert "refresh" in response.data


#Duplicate username test
@pytest.mark.django_db
def test_signup_duplicate_username():
    client = APIClient()

    User.objects.create_user(
        username="player2",
        email="p2@test.com",
        password="123"
    )

    response = client.post(
        "/api/signup/",
        {
            "username": "player2",
            "email": "new@test.com",
            "password": "123"
        },
        format="json"
    )

    assert response.status_code == 400


#Duplicate email test
@pytest.mark.django_db
def test_signup_duplicate_email():
    client = APIClient()

    User.objects.create_user(
        username="player3",
        email="dup@test.com",
        password="123"
    )

    response = client.post(
        "/api/signup/",
        {
            "username": "newuser",
            "email": "dup@test.com",
            "password": "123"
        },
        format="json"
    )

    assert response.status_code == 400

#Profile test
@pytest.mark.django_db
def test_profile_requires_authentication():
    client = APIClient()
    response = client.get("/api/profile/")
    assert response.status_code == 401


#Forgot password test
   #OTP sent test
@pytest.mark.django_db
def test_forgot_password_success():
    client = APIClient()

    User.objects.create_user(
        username="otpuser",
        email="otp@test.com",
        password="123"
    )

    response = client.post(
        "/api/forgot-password/",
        {"email": "otp@test.com"},
        format="json"
    )

    assert response.status_code == 200
    assert PasswordResetOTP.objects.count() == 1

   #User not found test
@pytest.mark.django_db
def test_forgot_password_user_not_found():
    client = APIClient()

    response = client.post(
        "/api/forgot-password/",
        {"email": "missing@test.com"},
        format="json"
    )

    assert response.status_code == 404


#Verify OTP
   #Correct OTP
@pytest.mark.django_db
def test_verify_otp_success():
    client = APIClient()

    user = User.objects.create_user(
        username="verify1",
        email="verify@test.com",
        password="123"
    )

    PasswordResetOTP.objects.create(
        user=user,
        otp="123456"
    )

    response = client.post(
        "/api/verify-otp/",
        {
            "email": "verify@test.com",
            "otp": "123456"
        },
        format="json"
    )

    assert response.status_code == 200

    #Invalid OTP
@pytest.mark.django_db
def test_verify_otp_invalid():
    client = APIClient()

    user = User.objects.create_user(
        username="verify2",
        email="verify2@test.com",
        password="123"
    )

    PasswordResetOTP.objects.create(
        user=user,
        otp="111111"
    )

    response = client.post(
        "/api/verify-otp/",
        {
            "email": "verify2@test.com",
            "otp": "999999"
        },
        format="json"
    )

    assert response.status_code == 400

    #Expired OTP
@pytest.mark.django_db
def test_verify_otp_expired():
    client = APIClient()

    user = User.objects.create_user(
        username="verify3",
        email="verify3@test.com",
        password="123"
    )

    otp = PasswordResetOTP.objects.create(
        user=user,
        otp="222222"
    )

    otp.created_at = timezone.now() - timedelta(minutes=6)
    otp.save()

    response = client.post(
        "/api/verify-otp/",
        {
            "email": "verify3@test.com",
            "otp": "222222"
        },
        format="json"
    )

    assert response.status_code == 400


#Reset Password
  #Reset success
@pytest.mark.django_db
def test_reset_password_success():
    client = APIClient()

    user = User.objects.create_user(
        username="reset1",
        email="reset@test.com",
        password="OldPass123"
    )

    PasswordResetOTP.objects.create(
        user=user,
        otp="333333"
    )

    response = client.post(
        "/api/reset-password/",
        {
            "email": "reset@test.com",
            "otp": "333333",
            "new_password": "NewPass123"
        },
        format="json"
    )

    user.refresh_from_db()

    assert response.status_code == 200
    assert user.check_password("NewPass123")

  #Invalid OTP
@pytest.mark.django_db
def test_reset_password_invalid_otp():
    client = APIClient()

    user = User.objects.create_user(
        username="reset2",
        email="reset2@test.com",
        password="OldPass"
    )

    response = client.post(
        "/api/reset-password/",
        {
            "email": "reset2@test.com",
            "otp": "000000",
            "new_password": "NewPass"
        },
        format="json"
    )

    assert response.status_code == 400

#FCM token registration test
@pytest.mark.django_db
def test_register_fcm_token_authenticated():
    client = APIClient()

    user = User.objects.create_user(
        username="fcmuser",
        password="123"
    )

    # login manually via token
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)

    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
    )

    response = client.post(
        "/api/register-fcm-token/",
        {"token": "fcm-test-token"},
        format="json"
    )

    assert response.status_code == 200
    assert FCMToken.objects.filter(user=user).exists()



