from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import random
from django.core.mail import send_mail
from .models import PasswordResetOTP
from datetime import timedelta
from django.utils import timezone
from .utils import send_sms
from django.contrib.auth import get_user_model
from .serializers import SignupSerializer, ForgotPasswordSerializer, VerifyOTPSerializer, ResetPasswordSerializer
from drf_yasg.utils import swagger_auto_schema
User = get_user_model()


# PROFILE (Protected)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    return Response({
        "username": request.user.username,
        "email": request.user.email
    })


#SIGNUP
@swagger_auto_schema(method='post',request_body=SignupSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
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


#FORGOT PASSWORD
@swagger_auto_schema(method='post',request_body=ForgotPasswordSerializer)
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


#VERIFY OTP
@swagger_auto_schema(method='post',request_body=VerifyOTPSerializer)
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


#RESET PASSWORD 
@swagger_auto_schema(method='post',request_body=ResetPasswordSerializer)
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    # Retrieve all users except the current user
    users = User.objects.exclude(id=request.user.id)
    user_list = [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
        for user in users
    ]
    return Response(user_list, status=200)
