from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

# 👤 Кастомная модель пользователя
class User(AbstractUser):
    phone = models.CharField(max_length=20)
    is_driver = models.BooleanField(default=False)
    car_model = models.CharField(max_length=50, blank=True)
    has_ac = models.BooleanField(default=False)
    hide_phone = models.BooleanField(default=False)
    show_phone = models.BooleanField(default=True)

    gender = models.CharField(
        max_length=10,
        choices=[('male', 'Мужчина'), ('female', 'Женщина')],
        null=True,
        blank=True,
    )

    def clean(self):
        # ❗ Не допускаем девушек в роли водителя
        if self.is_driver and self.gender == 'female':
            raise ValidationError("Таксист не может быть женщиной в этом приложении.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

# 🚕 Поездка
class Ride(models.Model):
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    driver = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    phone = models.CharField(max_length=20)
    seats = models.IntegerField()
    price = models.IntegerField(default=0)
    has_female_passenger = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.origin} → {self.destination}'

# 📦 Бронирование
class Booking(models.Model):
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE)
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

# 💬 Чат между двумя участниками
class Chat(models.Model):
    participants = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat ID {self.id}"

# 💬 Сообщения в чате
class ChatMessage(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages', null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender.username}: {self.message[:20]}"
