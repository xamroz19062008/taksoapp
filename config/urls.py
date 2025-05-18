from django.contrib import admin
from django.urls import path, include
from api.views import user_me  # если view с user_me находится в api/views.py

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/me/', user_me),

    # Основной API
    path('api/', include('api.urls')),

    # Авторизация через djoser
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),

    # Дополнительный endpoint для получения информации о текущем пользователе
    path('api/users/me/', user_me),
]
