from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
import random
from django.core.mail import send_mail
from .models import PasswordResetOTP

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
    email = request.data.get('email', '')

    if not username or not password:
        return Response({'error':'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(username=username).exists():
        return Response({'error':'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create user
    user = User.objects.create_user(username=username, password=password, email=email)

    # Create JWT tokens
    refresh = RefreshToken.for_user(user)

    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }, status=status.HTTP_201_CREATED)



#Forgot Password
@api_view(['POST'])
def forgot_password(request):
    email = request.data.get('email')

    try:
        user =User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error':'User not found.'},status=404)
    
    otp=str(random.randint(100000,999999))
    PasswordResetOTP.objects.create(user=user,otp=otp)
    
    send_mail(
        'Password Reset OTP',
        f'Your OTP is{otp}',
        'noreply@chessapp.com',
        [email],
    )
    

    return Response({'message':'OTP sent to email'})

#verify OTP
@api_view(['POST'])
def verify_otp(request):
    email=request.data.get('email')
    otp=request.data.get('otp')

    try:
        user = User.objects.gt(email=email)
        otp_obj=PasswordResetOTP.objects.filter(user=user, otp=otp).last()
    except:
        return Response({'error':'Invalid OTP'}, status=400)
    
    if not otp_obj:
        return Response({'error':'Invalid OTP'},status=400),
    return Response ({'message':'OTP verified'})

#Reset Password
@api_view(['POST'])
def reset_password(request):
    email=request.data.get('email')
    password=request.data.get('password')

    user =User.objects.get(email=email)
    user.set_password(password)
    user.save()

    PasswordResetOTP.objects.filter(user=user).delete()
    return Response({'meessage':'Password reset successful'})