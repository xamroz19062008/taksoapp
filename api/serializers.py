from rest_framework import serializers
from .models import User, Ride, Booking

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        # Используем create_user, чтобы пароль шифровался
        return User.objects.create_user(**validated_data)

class RideSerializer(serializers.ModelSerializer):
    driverUsername = serializers.CharField(source='driver.username', read_only=True)
    is_driver = serializers.BooleanField(source='driver.is_driver', read_only=True)

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
        ]






class BookingSerializer(serializers.ModelSerializer):
    passenger_username = serializers.CharField(source='passenger.username', read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'
