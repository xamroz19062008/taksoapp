from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, viewsets
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.utils.timezone import make_aware
from django.db.models import Q
from datetime import datetime

from .models import User, Ride, Booking, ChatMessage, ChatThread
from .serializers import (
    UserSerializer,
    RideSerializer,
    BookingSerializer,
    ChatMessageSerializer,
    ChatThreadSerializer
)

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

# === Регистрация ===
@api_view(['POST'])
def register_user(request):
    data = request.data
    required_fields = ['username', 'password', 'phone']
    for field in required_fields:
        if not data.get(field):
            return Response({'error': f'Missing field: {field}'}, status=400)

    if User.objects.filter(username=data['username']).exists():
        return Response({'error': 'Username already taken'}, status=400)

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
            'is_driver': user.is_driver,
            'has_ac': user.has_ac
        }, status=201)
    except Exception as e:
        return Response({'error': 'Server error', 'detail': str(e)}, status=500)

# === Логин ===
@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'is_driver': user.is_driver,
            'has_ac': user.has_ac
        })

    return Response({'error': 'Invalid credentials'}, status=401)

# === Создание поездки ===
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_ride(request):
    user = request.user
    data = request.data

    if user.is_driver and Ride.objects.filter(driver=user).exists():
        return Response({'error': 'Sizda allaqachon eʼlon mavjud'}, status=400)

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
        return Response(RideSerializer(ride).data, status=201)
    except Exception as e:
        return Response({'error': f"Eʼlon yaratishda xatolik: {e}"}, status=400)

# === Получение/обновление текущего пользователя ===
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_me(request):
    user = request.user
    if request.method == 'GET':
        return Response({
            'username': user.username,
            'is_driver': user.is_driver,
            'has_ac': user.has_ac
        })
    elif request.method == 'PATCH':
        user.has_ac = request.data.get('has_ac', user.has_ac)
        user.save()
        return Response({'has_ac': user.has_ac})


# === 💬 Чат: Получение сообщений между двумя участниками ===
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_messages(request, receiver_id):
    user = request.user

    # Найти или создать тред
    thread, _ = ChatThread.objects.get_or_create(
        sender=user,
        receiver_id=receiver_id
    )
    messages = ChatMessage.objects.filter(thread=thread).order_by('timestamp')
    serializer = ChatMessageSerializer(messages, many=True)
    return Response(serializer.data)

# === 💬 Чат: Отправка сообщения ===
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_chat_message(request):
    user = request.user
    receiver_id = request.data.get('receiver')

    # Найти или создать тред между sender и receiver
    thread, _ = ChatThread.objects.get_or_create(
        sender=user,
        receiver_id=receiver_id
    )

    message = ChatMessage.objects.create(
        thread=thread,
        sender=user,
        message=request.data.get('message')
    )

    return Response(ChatMessageSerializer(message).data, status=201)


# === 💬 Получить список тредов чата пользователя ===
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_threads(request):
    user = request.user
    threads = ChatThread.objects.filter(Q(sender=user) | Q(receiver=user)).distinct()
    serializer = ChatThreadSerializer(threads, many=True)
    return Response(serializer.data)
