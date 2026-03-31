from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EstacionRadioViewSet, OyenteActivoViewSet, EstadisticaRadioViewSet,
    streaming_proxy, api_chat_mensajes, api_chat_usuarios_online,
    api_chat_eliminar_mensaje, api_chat_bloquear_usuario, api_chat_desbloquear_usuario,
    api_chat_advertir_usuario, api_chat_verificar_bloqueo, api_chat_lista_bloqueados,
    api_chat_advertencias_usuario
)

router = DefaultRouter()
router.register(r'estacion', EstacionRadioViewSet, basename='estacion')
router.register(r'oyentes', OyenteActivoViewSet, basename='oyentes')
router.register(r'estadisticas', EstadisticaRadioViewSet, basename='estadisticas')

urlpatterns = [
    path('', include(router.urls)),
    path('stream/', streaming_proxy, name='streaming_proxy'),
    # Chat en vivo
    path('chat/mensajes/', api_chat_mensajes, name='chat_mensajes'),
    path('chat/mensajes/<int:mensaje_id>/', api_chat_eliminar_mensaje, name='chat_eliminar_mensaje'),
    path('chat/usuarios-online/', api_chat_usuarios_online, name='chat_usuarios_online'),
    # Moderación de chat
    path('chat/bloquear/', api_chat_bloquear_usuario, name='chat_bloquear_usuario'),
    path('chat/desbloquear/', api_chat_desbloquear_usuario, name='chat_desbloquear_usuario'),
    path('chat/advertir/', api_chat_advertir_usuario, name='chat_advertir_usuario'),
    path('chat/bloqueados/', api_chat_lista_bloqueados, name='chat_lista_bloqueados'),
    path('chat/bloqueados/<str:username>/', api_chat_verificar_bloqueo, name='chat_verificar_bloqueo'),
    path('chat/advertencias/<str:username>/', api_chat_advertencias_usuario, name='chat_advertencias_usuario'),
]
