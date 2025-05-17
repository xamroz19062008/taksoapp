from django.contrib.auth.models import AbstractUser
from django.db import models

# 👤 Кастомная модель пользователя
class User(AbstractUser):
    phone = models.CharField(max_length=20)
    is_driver = models.BooleanField(default=False)
    car_model = models.CharField(max_length=100, blank=True, null=True)
    has_ac = models.BooleanField(default=False)

    def __str__(self):
        return self.username

# 🚕 Поездка
class Ride(models.Model):
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    driver = models.ForeignKey(User, on_delete=models.CASCADE)  # ← если удалить водителя, поездка тоже удалится
    datetime = models.DateTimeField()
    phone = models.CharField(max_length=20)
    seats = models.IntegerField()
    price = models.IntegerField(default=0)  # ← сумма в суммах

    def __str__(self):
        return f'{self.origin} → {self.destination}'

# 📦 Бронирование (пассажир бронирует поездку)
class Booking(models.Model):
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE)  # ← если поездка удаляется, бронирование исчезает
    passenger = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Ожидание'),
            ('confirmed', 'Подтверждено')
        ],
        default='pending'
    )

    def __str__(self):
        return f'{self.passenger.username} - {self.ride}'

# 💬 Сообщения в чате
class ChatMessage(models.Model):
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE)  # ← чат связан с поездкой
    sender = models.ForeignKey(User, on_delete=models.CASCADE)  # ← кто отправил
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender.username}: {self.message[:20]}...'
