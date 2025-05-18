from rest_framework import serializers
from .models import User, Ride, Booking

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'has_ac': {'required': False},  # ✅ разрешить обновление кондиционера
            'password': {'write_only': True}  # ✅ скрыть пароль при выводе
        }

    def create(self, validated_data):
        # Используем create_user для шифрования пароля
        return User.objects.create_user(**validated_data)


class RideSerializer(serializers.ModelSerializer):
    driverUsername = serializers.CharField(source='driver.username', read_only=True)
    is_driver = serializers.BooleanField(source='driver.is_driver', read_only=True)
    has_ac = serializers.BooleanField(source='driver.has_ac', read_only=True)

    class Meta:
        model = Ride
        fields = [
            'id',
            'origin',
            'destination',
            'phone',
            'seats',
            'price',
            'datetime',
            'driver',
            'driverUsername',
            'is_driver',
            'has_ac',
        ]


class BookingSerializer(serializers.ModelSerializer):
    passenger_username = serializers.CharField(source='passenger.username', read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'
