from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from . import database

# Create your views here. 


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    return Response(
        {
            "username":request.user.username,
            "email":request.user.email
        }
    )


@api_view(['POST'])
def signup(request):
    username=request.data.get('username')
    password=request.data.get('password')
    email=request.data.get('email','')

    if not username or not password:
        return Response({'error':'Username and password ae required'},status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(username=username).exists():
        return Response({'error':'Username already exists'},status=status.HTTP_400_BAD_REQUEST)
    user - User.objects.create_user(username=username, password=password, email=email)

    #Create jwt tokens
    refresh=RefreshToken.for_user(user)

    return Response({
        'refresh':str(refresh),
        'access':str(refresh.access_token)
    },status=status.HTTP_201_CREATED)
