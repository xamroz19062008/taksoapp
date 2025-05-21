from rest_framework import serializers
from .models import User, Ride, Booking, ChatMessage, Chat

# ✅ Сериализатор сообщений чата
class ChatMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'chat', 'sender', 'sender_username', 'message', 'timestamp', 'is_read']
        read_only_fields = ['id', 'chat', 'sender', 'sender_username', 'timestamp', 'is_read']

# ✅ Сериализатор чата
class ChatSerializer(serializers.ModelSerializer):
    participants_usernames = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ['id', 'participants_usernames', 'created_at']

    def get_participants_usernames(self, obj):
        return [user.username for user in obj.participants.all()]

# ✅ Сериализатор пользователя
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'has_ac': {'required': False},
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

# ✅ Сериализатор поездки
class RideSerializer(serializers.ModelSerializer):
    driver = serializers.IntegerField(source='driver.id', read_only=True)
    driverUsername = serializers.CharField(source='driver.username', read_only=True)
    is_driver = serializers.BooleanField(source='driver.is_driver', read_only=True)
    has_ac = serializers.BooleanField(source='driver.has_ac', read_only=True)
    car_model = serializers.CharField(source='driver.car_model', read_only=True)

    class Meta:
        model = Ride
        fields = '__all__'

# ✅ Сериализатор бронирования
class BookingSerializer(serializers.ModelSerializer):
    passenger_username = serializers.CharField(source='passenger.username', read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'
