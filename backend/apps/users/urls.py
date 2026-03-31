from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para el ViewSet
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')

app_name = 'users'

urlpatterns = [
    # URLs API (sin autenticación)
    path('register/', views.api_register, name='api_register'),
    path('login/', views.api_login, name='api_login'),
    
    # URLs para recuperación de contraseña
    path('password-reset/', views.api_password_reset_request, name='api_password_reset_request'),
    path('password-reset-confirm/', views.api_password_reset_confirm, name='api_password_reset_confirm'),
    
    # URLs del ViewSet
    path('', include(router.urls)),
]
