from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    RideViewSet,
    BookingViewSet,
    register_user,
    login_user,
    create_ride,
    get_user_threads,
    get_chat_messages,
    send_chat_message,
)

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('rides', RideViewSet)
router.register('bookings', BookingViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # 🔐 Auth
    path('register/', register_user),
    path('login/', login_user),

    # 🚕 Ride
    path('custom/create_ride/', create_ride),

    # 💬 Chat (новая система)
    path('chat/threads/', get_user_threads),
    path('chat/<int:receiver_id>/messages/', get_chat_messages),
    path('chat/send/', send_chat_message),
]
