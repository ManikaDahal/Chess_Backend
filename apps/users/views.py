from django.utils import timezone
from datetime import timedelta
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .serializers import UserSerializer

def get_rank_name(coins):
    if coins <= 1000: return "Novice"
    if coins <= 3000: return "Amateur"
    if coins <= 7000: return "Pro"
    if coins <= 15000: return "Master"
    return "Grandmaster"

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    can_claim = True
    if user.last_gift_claim:
        can_claim = timezone.now() > user.last_gift_claim + timedelta(hours=24)
        
    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "coins": user.coins,
        "rank_name": get_rank_name(user.coins),
        "can_claim_gift": can_claim
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_coins(request):
    amount = request.data.get('amount', 0)
    user = request.user
    user.coins += int(amount)
    user.save()
    return Response({
        "coins": user.coins,
        "rank_name": get_rank_name(user.coins)
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def claim_daily_gift(request):
    user = request.user
    now = timezone.now()
    
    if user.last_gift_claim and now < user.last_gift_claim + timedelta(hours=24):
        return Response({"error": "Gift already claimed. Come back later!"}, status=400)
        
    user.coins += 200
    user.last_gift_claim = now
    user.save()
    
    return Response({
        "message": "Daily gift claimed! +200 gold",
        "coins": user.coins,
        "rank_name": get_rank_name(user.coins)
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    users = CustomUser.objects.exclude(id=request.user.id)
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=200)
