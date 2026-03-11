from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from .models import FCMToken
from .serializers import FCMTokenSerializer

@swagger_auto_schema(method='post', request_body=FCMTokenSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_fcm_token(request):
    serializer = FCMTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    token = serializer.validated_data['token']
    
    fcm_token, created = FCMToken.objects.update_or_create(
        token=token,
        defaults={'user': request.user}
    )
    
    return Response({"message": "FCM token registered successfully"}, status=200)
