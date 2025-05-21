from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    RideViewSet,
    BookingViewSet,
    register_user,
    login_user,
    create_ride,
    user_me,
    get_user_threads,       # ✅ список чатов
    get_chat_messages,      # ✅ сообщения между двумя пользователями
    send_chat_message       # ✅ отправка сообщения
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

    # 👤 Profile
    path('users/me/', user_me),

    # 💬 Chat (новая система)
    path('chat/threads/', get_user_threads),                    # ✅ список всех чатов пользователя
    path('chat/<int:receiver_id>/messages/', get_chat_messages),  # ✅ сообщения между двумя людьми
    path('chat/send/', send_chat_message),                      # ✅ отправить сообщение
]
