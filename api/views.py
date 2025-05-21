from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, viewsets
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.utils.timezone import make_aware
from datetime import datetime

from .models import User, Ride, Booking, ChatMessage, Chat
from .serializers import (
    UserSerializer,
    RideSerializer,
    BookingSerializer,
    ChatMessageSerializer,
)

# === ViewSets ===
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['get', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
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
        user.show_phone = bool(data.get('show_phone', True))
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


# === Получить чат между двумя пользователями ===
def get_or_create_chat(user1, user2):
    chats = Chat.objects.filter(participants=user1).filter(participants=user2)
    if chats.exists():
        return chats.first()
    else:
        chat = Chat.objects.create()
        chat.participants.add(user1, user2)
        return chat


# === Получить сообщения чата и отметить как прочитанные ===
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_messages(request, receiver_id):
    user = request.user
    try:
        receiver = User.objects.get(id=receiver_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    chat = get_or_create_chat(user, receiver)

    ChatMessage.objects.filter(chat=chat, sender=receiver, is_read=False).update(is_read=True)

    messages = ChatMessage.objects.filter(chat=chat).order_by('timestamp')
    serializer = ChatMessageSerializer(messages, many=True)
    return Response(serializer.data)


# === Отправить сообщение ===
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_chat_message(request):
    user = request.user
    receiver_id = request.data.get('receiver')

    if not receiver_id:
        return Response({'error': 'Receiver ID is required'}, status=400)

    try:
        receiver = User.objects.get(id=receiver_id)
    except User.DoesNotExist:
        return Response({'error': 'Receiver not found'}, status=404)

    chat = get_or_create_chat(user, receiver)

    message = ChatMessage.objects.create(
        chat=chat,
        sender=user,
        message=request.data.get('message'),
        is_read=False
    )

    return Response(ChatMessageSerializer(message).data, status=201)


# === Получить список чатов пользователя ===
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_chats(request):
    user = request.user
    chats = Chat.objects.filter(participants=user)
    result = []

    for chat in chats:
        last_message = chat.messages.order_by('-timestamp').first()
        other = chat.participants.exclude(id=user.id).first()
        result.append({
            'chat_id': chat.id,
            'last_message': last_message.message if last_message else '',
            'timestamp': last_message.timestamp if last_message else '',
            'sender_username': last_message.sender.username if last_message else '',
            'receiver_username': other.username if other else '',
            'receiver': other.id if other else '',
        })

    return Response(result)


# === Получить треды чатов пользователя ===
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_threads(request):
    user = request.user
    threads = Chat.objects.filter(participants=user).distinct()
    data = []
    for chat in threads:
        other = chat.participants.exclude(id=user.id).first()
        data.append({
            'id': chat.id,
            'participants_usernames': [u.username for u in chat.participants.all()],
            'created_at': chat.created_at,
            'receiver': other.id if other else None
        })
    return Response(data)


# === Получить количество непрочитанных сообщений ===
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unread_message_count(request):
    user = request.user
    count = ChatMessage.objects.filter(chat__participants=user, is_read=False).exclude(sender=user).count()
    return Response({'unread_count': count})
