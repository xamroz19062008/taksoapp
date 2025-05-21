from rest_framework import serializers
from .models import User, Ride, Booking, ChatMessage, ChatThread

# ✅ ChatThread Serializer
class ChatThreadSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    receiver_username = serializers.CharField(source='receiver.username', read_only=True)

    class Meta:
        model = ChatThread
        fields = ['id', 'sender', 'receiver', 'sender_username', 'receiver_username']


# ✅ ChatMessage Serializer
class ChatMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'thread', 'sender', 'sender_username', 'message', 'timestamp']


# ✅ User Serializer
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


# ✅ Ride Serializer
class RideSerializer(serializers.ModelSerializer):
    driverUsername = serializers.CharField(source='driver.username', read_only=True)
    is_driver = serializers.BooleanField(source='driver.is_driver', read_only=True)
    has_ac = serializers.BooleanField(source='driver.has_ac', read_only=True)
    car_model = serializers.CharField(source='driver.car_model', read_only=True)

    class Meta:
        model = Ride
        fields = '__all__'


# ✅ Booking Serializer
class BookingSerializer(serializers.ModelSerializer):
    passenger_username = serializers.CharField(source='passenger.username', read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'
