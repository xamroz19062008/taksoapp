from django.contrib import admin
from .models import User, Ride, Booking

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'phone', 'is_driver', 'car_model', 'has_ac')
    search_fields = ('username', 'phone')
    list_filter = ('is_driver', 'has_ac')

@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ('origin', 'destination', 'driver', 'datetime', 'seats')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('passenger', 'ride')  # 'created_at' убран
    search_fields = ('passenger__username',)
