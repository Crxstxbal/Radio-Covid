from django.urls import path
from . import views
from . import user_views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_home, name='home'),
    path('estacion/', views.configurar_estacion, name='configurar_estacion'),
    
    # Oyentes
    path('oyentes/', views.ver_oyentes, name='ver_oyentes'),
    
    # Estadísticas
    path('estadisticas/', views.ver_estadisticas, name='ver_estadisticas'),
    
    # Chat
    path('chat/', views.chat_moderacion, name='ver_chat'),
    path('chat/moderacion/', views.chat_moderacion, name='chat_moderacion'),
    path('chat/bloqueados/', views.chat_bloqueados, name='chat_bloqueados'),
    path('chat/historial/', views.chat_historial, name='chat_historial'),
    path('chat/eliminar/<int:mensaje_id>/', views.eliminar_mensaje, name='eliminar_mensaje'),
    path('chat/banear/<str:username>/', views.banear_usuario, name='banear_usuario'),
    path('chat/desbloquear/<str:username>/', views.desbloquear_usuario, name='desbloquear_usuario'),
    path('chat/advertir/<str:username>/', views.advertir_usuario, name='advertir_usuario'),
    
    # Gestión de usuarios (desde user_views)
    path('usuarios/', user_views.ver_usuarios, name='ver_usuarios'),
    path('usuarios/<int:user_id>/', user_views.detalle_usuario, name='detalle_usuario'),
    path('usuarios/<int:user_id>/toggle-staff/', user_views.toggle_usuario_staff, name='toggle_usuario_staff'),
    path('usuarios/<int:user_id>/toggle-activo/', user_views.toggle_usuario_activo, name='toggle_usuario_activo'),
]
