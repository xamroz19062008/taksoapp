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


# ✅ Сериализатор пользователя с валидацией пола
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'has_ac': {'required': False},
            'show_phone': {'required': False},
            'hide_phone': {'required': False},
            'car_model': {'required': False},
            'password': {'write_only': True},
            'gender': {'required': False},
        }

    def create(self, validated_data):
        # ✅ Проверка: если это не водитель, то gender обязателен
        if not validated_data.get("is_driver") and validated_data.get("gender") is None:
            raise serializers.ValidationError("Jins majburiy (faqat yo‘lovchilar uchun)")
        return User.objects.create_user(**validated_data)


# ✅ Сериализатор поездки
class RideSerializer(serializers.ModelSerializer):
    driver = serializers.IntegerField(source='driver.id', read_only=True)
    driverUsername = serializers.CharField(source='driver.username', read_only=True)
    is_driver = serializers.BooleanField(source='driver.is_driver', read_only=True)
    has_ac = serializers.BooleanField(source='driver.has_ac', read_only=True)
    car_model = serializers.CharField(source='driver.car_model', read_only=True)
    show_phone = serializers.BooleanField(source='driver.show_phone', read_only=True)
    driver_gender = serializers.CharField(source='driver.gender', read_only=True)
    has_female_passenger = serializers.BooleanField(required=False, allow_null=True)
    phone = serializers.SerializerMethodField()  # 👈 показываем только если разрешено

    class Meta:
        model = Ride
        fields = '__all__'

    def get_phone(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        if obj.driver == user or obj.driver.show_phone:
            return obj.phone
        return None


# ✅ Сериализатор бронирования
class BookingSerializer(serializers.ModelSerializer):
    passenger_username = serializers.CharField(source='passenger.username', read_only=True)
    passenger_gender = serializers.CharField(source='passenger.gender', read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'
