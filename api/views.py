from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, viewsets
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.utils.timezone import make_aware
from datetime import datetime

from .models import User, Ride, Booking
from .serializers import UserSerializer, RideSerializer, BookingSerializer

# === ViewSets ===
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all().order_by('-datetime')
    serializer_class = RideSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

# === Регистрация пользователя ===
@api_view(['POST'])
def register_user(request):
    data = request.data
    print("📥 Пришло от клиента:", data)

    required_fields = ['username', 'password', 'phone']
    for field in required_fields:
        if not data.get(field):
            return Response({'error': f'Missing field: {field}'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=data['username']).exists():
        return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.create_user(
            username=data['username'],
            password=data['password']
        )
        user.phone = data['phone']
        user.is_driver = bool(data.get('is_driver', False))
        user.car_model = data.get('car_model') or ''
        user.has_ac = bool(data.get('has_ac', False))
        user.save()

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'status': 'created',
            'token': token.key,
            'is_driver': user.is_driver
        }, status=201)
    except Exception as e:
        print("❌ Ошибка при регистрации:", str(e))
        return Response({'error': 'Server error', 'detail': str(e)}, status=500)

# === Логин пользователя ===
@api_view(['POST'])
def login_user(request):
    data = request.data
    username = data.get('username')
    password = data.get('password')
    print("🔐 Попытка входа:", data)

    if not username or not password:
        return Response({'error': 'Username and password required'}, status=400)

    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'is_driver': user.is_driver
        }, status=200)

    return Response({'error': 'Invalid credentials'}, status=401)

# === Создание поездки ===
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_ride(request):
    user = request.user
    data = request.data
    print("📨 Yangi eʼlon:", data)

    # Проверка только для таксистов
    if user.is_driver and Ride.objects.filter(driver=user).exists():
        return Response({'error': 'У вас уже есть активное объявление'}, status=400)

    try:
        aware_datetime = make_aware(datetime.fromisoformat(data['datetime']))

        ride = Ride.objects.create(
            origin=data['origin'],
            destination=data['destination'],
            phone=data['phone'],
            seats=int(data['seats']),
            price=int(data['price']) if user.is_driver else 0,
            datetime=aware_datetime,
            driver=user
        )
        serializer = RideSerializer(ride)
        return Response(serializer.data, status=201)
    except Exception as e:
        print("❌ Xatolik:", str(e))
        return Response({'error': f"Eʼlon yaratishda xatolik: {e}"}, status=400)
