from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    RideViewSet,
    BookingViewSet,
    register_user,
    login_user,
    create_ride,
    user_me,  # ✅ добавлено
)

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('rides', RideViewSet)
router.register('bookings', BookingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', register_user),
    path('login/', login_user),
    path('custom/create_ride/', create_ride),
    path('users/me/', user_me),  # ✅ обязательно для PATCH/GET профиля
]
