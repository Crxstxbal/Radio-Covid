from rest_framework import serializers
from .models import EstacionRadio, OyenteActivo, EstadisticaRadio, MensajeChat, UsuarioBloqueado, AdvertenciaChat


class EstacionRadioSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = EstacionRadio
        fields = [
            'id', 'nombre', 'descripcion', 'stream_url', 'logo', 'logo_url',
            'activa', 'fecha_creacion', 'fecha_actualizacion'
        ]

    def get_logo_url(self, obj):
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None


class OyenteActivoSerializer(serializers.ModelSerializer):
    tiempo_conectado = serializers.SerializerMethodField()

    class Meta:
        model = OyenteActivo
        fields = [
            'id', 'session_key', 'ip_address', 'user_agent',
            'fecha_conexion', 'ultima_actividad', 'esta_escuchando',
            'tiempo_conectado'
        ]

    def get_tiempo_conectado(self, obj):
        from django.utils import timezone
        delta = timezone.now() - obj.fecha_conexion
        return str(delta).split('.')[0]  # Formato HH:MM:SS


class EstadisticaRadioSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadisticaRadio
        fields = [
            'id', 'fecha', 'oyentes_maximos_simultaneos',
            'total_conexiones', 'tiempo_promedio_escucha'
        ]


class MensajeChatSerializer(serializers.ModelSerializer):
    """Serializer para mensajes de chat"""
    
    class Meta:
        model = MensajeChat
        fields = ['id', 'usuario', 'mensaje', 'fecha_envio', 'ip_address']
        read_only_fields = ['id', 'fecha_envio', 'ip_address']


class UsuarioBloqueadoChatSerializer(serializers.ModelSerializer):
    """Serializer para usuarios bloqueados del chat"""
    
    class Meta:
        model = UsuarioBloqueado
        fields = [
            'id', 'username', 'razon', 'fecha_bloqueo',
            'fecha_expiracion', 'bloqueado_por', 'activo'
        ]
        read_only_fields = ['id', 'fecha_bloqueo']


class AdvertenciaChatSerializer(serializers.ModelSerializer):
    """Serializer para advertencias de chat"""
    
    class Meta:
        model = AdvertenciaChat
        fields = [
            'id', 'username', 'advertido_por', 'razon', 'mensaje_original',
            'fecha_advertencia', 'leida'
        ]
        read_only_fields = ['id', 'fecha_advertencia']
