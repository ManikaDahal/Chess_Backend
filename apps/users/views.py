from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .serializers import UserSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    return Response({
        "id": request.user.id,
        "username": request.user.username,
        "email": request.user.email
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    users = CustomUser.objects.exclude(id=request.user.id)
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=200)
