from django.urls import path
from . import views

app_name = 'users_templates'

urlpatterns = [
    # URLs para templates
    path('registro/', views.register_view, name='register'),
    path('iniciar-sesion/', views.login_view, name='login'),
    path('perfil/', views.profile_view, name='profile'),
    path('cerrar-sesion/', views.logout_view, name='logout'),
]
