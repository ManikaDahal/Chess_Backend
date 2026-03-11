from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import random
from django.core.mail import send_mail
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_yasg.utils import swagger_auto_schema

# Note: We'll need a way to reach the utils.py. For now, we'll import from chess_python
# but eventually it should be moved to a shared location or duplicated if it's app-specific.
from chess_python.utils import send_sms
from .models import PasswordResetOTP
from .serializers import (
    SignupSerializer, ForgotPasswordSerializer, VerifyOTPSerializer, 
    ResetPasswordSerializer, EmailTokenObtainPairSerializer
)

from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url

class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
    throttle_scope = 'login'

User = get_user_model()

@api_view(['GET'])
@permission_classes([AllowAny])
def get_captcha(request):
    hashkey = CaptchaStore.generate_key()
    image_url = request.build_absolute_uri(captcha_image_url(hashkey))
    return Response({
        'captcha_hash': hashkey,
        'captcha_image_url': image_url
    })

@swagger_auto_schema(method='post', request_body=SignupSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([ScopedRateThrottle])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data['username']
    password = serializer.validated_data['password']
    email = serializer.validated_data['email']

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=400)

    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already registered'}, status=400)

    user = User.objects.create_user(username=username, password=password, email=email)
    refresh = RefreshToken.for_user(user)

    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }, status=201)

@swagger_auto_schema(method='post', request_body=ForgotPasswordSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    serializer = ForgotPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data.get('email')
    phone = serializer.validated_data.get('phone')

    try:
        user = User.objects.get(email=email) if email else User.objects.get(phone=phone)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    otp = str(random.randint(100000, 999999))
    PasswordResetOTP.objects.create(user=user, otp=otp)

    if email:
        send_mail(
            'Password Reset OTP',
            f'Your OTP is {otp}',
            'noreply@chessapp.com',
            [email],
        )
    if phone:
        send_sms(phone, f'Your OTP is {otp}')

    return Response({'message': 'OTP sent successfully'}, status=200)

@swagger_auto_schema(method='post', request_body=VerifyOTPSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    serializer = VerifyOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data.get('email')
    phone = serializer.validated_data.get('phone')
    otp = serializer.validated_data['otp']

    try:
        user = User.objects.get(email=email) if email else User.objects.get(phone=phone)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    otp_obj = PasswordResetOTP.objects.filter(user=user, otp=otp).last()
    if not otp_obj:
        return Response({'error': 'Invalid OTP'}, status=400)

    if otp_obj.created_at + timedelta(minutes=5) < timezone.now():
        return Response({'error': 'OTP expired'}, status=400)

    return Response({'message': 'OTP verified'}, status=200)

@swagger_auto_schema(method='post', request_body=ResetPasswordSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    serializer = ResetPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data.get('email')
    phone = serializer.validated_data.get('phone')
    otp = serializer.validated_data['otp']
    new_password = serializer.validated_data['new_password']

    try:
        user = User.objects.get(email=email) if email else User.objects.get(phone=phone)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    otp_obj = PasswordResetOTP.objects.filter(user=user, otp=otp).last()
    if not otp_obj or otp_obj.created_at + timedelta(minutes=5) < timezone.now():
        return Response({'error': 'Invalid or expired OTP'}, status=400)

    user.set_password(new_password)
    user.save()
    PasswordResetOTP.objects.filter(user=user).delete()

    refresh = RefreshToken.for_user(user)

    return Response({
        'message': 'Password reset successful',
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    }, status=200)
