from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import random
from django.core.mail import send_mail
from .models import PasswordResetOTP
from datetime import timedelta
from django.utils import timezone
from twilio.rest import Client
import os
from .utils import send_sms
from django.contrib.auth import get_user_model
User = get_user_model()





# Profile API (protected)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    return Response({
        "username": request.user.username,
        "email": request.user.email
    })


# Signup API
@api_view(['POST'])
def signup(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    if not username or not password or not email:
        return Response({'error': 'All fields are required'}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=400)

 
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already registered'}, status=400)

    user = User.objects.create_user(
        username=username,
        password=password,
        email=email
    )

    refresh = RefreshToken.for_user(user)

    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }, status=201)



#Forgot Password
@api_view(['POST'])
def forgot_password(request):
    email = request.data.get('email')
    phone = request.data.get('phone')

    if not email and not phone:
        return Response({'error': 'Email or Phone is required'}, status=400)

    try:
        if email:
            user = User.objects.get(email=email)
        else:
            user = User.objects.get(phone=phone)
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


#verify OTP
@api_view(['POST'])
def verify_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')

    if not email or not otp:
        return Response({'error': 'Email and OTP are required'}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid email'}, status=400)

    otp_obj = PasswordResetOTP.objects.filter(user=user, otp=otp).last()

    if not otp_obj:
        return Response({'error': 'Invalid OTP'}, status=400)

    if otp_obj.created_at + timedelta(minutes=5) < timezone.now():
        return Response({'error': 'OTP expired'}, status=400)

    return Response({'message': 'OTP verified'}, status=200)



#Reset Password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

@api_view(['POST'])
def reset_password(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    
    user.set_password(password)
    user.save()

    PasswordResetOTP.objects.filter(user=user).delete()

    
    refresh = RefreshToken.for_user(user)
    access = str(refresh.access_token)

    
    return Response({
        'message': 'Password reset successful',
        'access': access,
        'refresh': str(refresh)
    }, status=status.HTTP_200_OK)
