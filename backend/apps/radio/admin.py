from django.contrib import admin
from .models import EstacionRadio, OyenteActivo, EstadisticaRadio, MensajeChat


@admin.register(EstacionRadio)
class EstacionRadioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activa', 'fecha_creacion']
    list_filter = ['activa', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(OyenteActivo)
class OyenteActivoAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'fecha_conexion', 'ultima_actividad', 'esta_escuchando']
    list_filter = ['esta_escuchando', 'fecha_conexion']
    search_fields = ['ip_address', 'session_key']
    readonly_fields = ['session_key', 'fecha_conexion', 'ultima_actividad']
    
    def has_add_permission(self, request):
        return False  # No permitir agregar manualmente


@admin.register(EstadisticaRadio)
class EstadisticaRadioAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'oyentes_maximos_simultaneos', 'total_conexiones']
    list_filter = ['fecha']
    readonly_fields = ['fecha']
    
    def has_add_permission(self, request):
        return False  # No permitir agregar manualmente


@admin.register(MensajeChat)
class MensajeChatAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'mensaje_corto', 'fecha_envio', 'ip_address']
    list_filter = ['fecha_envio']
    search_fields = ['usuario', 'mensaje', 'ip_address']
    readonly_fields = ['fecha_envio']
    ordering = ['-fecha_envio']
    
    def mensaje_corto(self, obj):
        """Muestra los primeros 50 caracteres del mensaje"""
        return obj.mensaje[:50] + '...' if len(obj.mensaje) > 50 else obj.mensaje
    mensaje_corto.short_description = 'Mensaje'
    
    def has_add_permission(self, request):
        return False  # Los mensajes solo se crean desde el chat
