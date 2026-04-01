from django.db import models
from django.utils import timezone
from django.conf import settings


class EstacionRadio(models.Model):
    """Modelo para configuración de la estación de radio"""
    nombre = models.CharField(max_length=200, default="Tu Radio")
    descripcion = models.TextField(blank=True)
    stream_url = models.URLField(max_length=500, help_text="URL del streaming de la radio")
    logo = models.ImageField(upload_to='radio/', blank=True, null=True)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Estación de Radio"
        verbose_name_plural = "Estaciones de Radio"

    def __str__(self):
        return self.nombre

    @classmethod
    def get_activa(cls):
        """Obtener la estación activa"""
        return cls.objects.filter(activa=True).first()


class OyenteActivo(models.Model):
    """Modelo para registrar oyentes activos"""
    session_key = models.CharField(max_length=40, unique=True)
    usuario = models.CharField(max_length=150, blank=True, null=True, help_text="Nombre de usuario si está autenticado")
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    fecha_conexion = models.DateTimeField(auto_now_add=True)
    ultima_actividad = models.DateTimeField(auto_now=True)
    esta_escuchando = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Oyente Activo"
        verbose_name_plural = "Oyentes Activos"

    def __str__(self):
        return f"{self.usuario or 'Anónimo'} - {self.fecha_conexion}"

    @classmethod
    def limpiar_inactivos(cls, minutos=10):
        """Limpiar oyentes inactivos por más de X minutos"""
        limite = timezone.now() - timezone.timedelta(minutes=minutos)
        cls.objects.filter(ultima_actividad__lt=limite).delete()

    @classmethod
    def obtener_conteo_actual(cls):
        """Obtener conteo de oyentes activos"""
        cls.limpiar_inactivos()
        return cls.objects.filter(esta_escuchando=True).count()


class EstadisticaRadio(models.Model):
    """Modelo para estadísticas de la radio"""
    fecha = models.DateField()
    oyentes_maximos_simultaneos = models.PositiveIntegerField(default=0)
    total_conexiones = models.PositiveIntegerField(default=0)
    tiempo_promedio_escucha = models.DurationField(null=True, blank=True)

    class Meta:
        verbose_name = "Estadística de Radio"
        verbose_name_plural = "Estadísticas de Radio"
        ordering = ['-fecha']
        unique_together = ['fecha']

    def __str__(self):
        return f"Estadísticas {self.fecha}"


class MensajeChat(models.Model):
    """Modelo para mensajes del chat en vivo"""
    usuario = models.CharField(max_length=150)
    mensaje = models.TextField(max_length=500)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Mensaje de Chat"
        verbose_name_plural = "Mensajes de Chat"
        ordering = ['-fecha_envio']
    
    def __str__(self):
        return f"{self.usuario}: {self.mensaje[:50]}..."
    
    def to_dict(self):
        """Convertir a diccionario para WebSocket/API"""
        return {
            'id': self.id,
            'usuario': self.usuario,
            'mensaje': self.mensaje,
            'timestamp': self.fecha_envio.isoformat()
        }


class UsuarioBloqueadoChat(models.Model):
    """Modelo para usuarios bloqueados del chat"""
    username = models.CharField(max_length=150, unique=True)
    bloqueado_por = models.CharField(max_length=150, blank=True, help_text="Usuario admin que bloqueó")
    razon = models.TextField(blank=True, help_text="Razón del bloqueo")
    fecha_bloqueo = models.DateTimeField(auto_now_add=True)
    fecha_desbloqueo = models.DateTimeField(null=True, blank=True, help_text="Fecha de desbloqueo automático (opcional)")
    permanente = models.BooleanField(default=True, help_text="Bloqueo permanente o temporal")
    activo = models.BooleanField(default=True, help_text="Si el bloqueo está activo")
    
    class Meta:
        verbose_name = "Usuario Bloqueado del Chat"
        verbose_name_plural = "Usuarios Bloqueados del Chat"
        ordering = ['-fecha_bloqueo']
    
    def __str__(self):
        tipo = "Permanente" if self.permanente else "Temporal"
        return f"{self.username} - {tipo} - {'Activo' if self.activo else 'Inactivo'}"
    
    @classmethod
    def esta_bloqueado(cls, username):
        """Verificar si un usuario está bloqueado"""
        from django.utils import timezone
        bloqueo = cls.objects.filter(
            username=username,
            activo=True
        ).first()
        
        if not bloqueo:
            return False
        
        # Si tiene fecha de desbloqueo y ya pasó, desactivar el bloqueo
        if bloqueo.fecha_desbloqueo and bloqueo.fecha_desbloqueo < timezone.now():
            bloqueo.activo = False
            bloqueo.save()
            return False
        
        return True


class AdvertenciaChat(models.Model):
    """Modelo para advertencias a usuarios del chat"""
    username = models.CharField(max_length=150, db_index=True)
    advertido_por = models.CharField(max_length=150, blank=True, help_text="Usuario admin que dio la advertencia")
    razon = models.TextField(help_text="Razón de la advertencia")
    mensaje_original = models.TextField(blank=True, help_text="Mensaje que causó la advertencia")
    fecha_advertencia = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False, help_text="Si el usuario la ha visto")
    
    class Meta:
        verbose_name = "Advertencia de Chat"
        verbose_name_plural = "Advertencias de Chat"
        ordering = ['-fecha_advertencia']
    
    def __str__(self):
        return f"Advertencia a {self.username} - {self.fecha_advertencia.strftime('%d/%m/%Y %H:%M')}"
    
    @classmethod
    def contar_advertencias_activas(cls, username):
        """Contar advertencias no leídas de un usuario"""
        return cls.objects.filter(username=username, leida=False).count()


class UsuarioBloqueado(models.Model):
    """Modelo para usuarios bloqueados del chat"""
    username = models.CharField(max_length=150, unique=True, help_text="Nombre de usuario bloqueado")
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="IP opcional del usuario")
    razon = models.TextField(help_text="Razón del bloqueo")
    fecha_bloqueo = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(null=True, blank=True, help_text="Fecha de desbloqueo automático (opcional)")
    bloqueado_por = models.CharField(max_length=150, help_text="Administrador que realizó el bloqueo")
    activo = models.BooleanField(default=True, help_text="Si el bloqueo está activo")
    
    class Meta:
        verbose_name = "Usuario Bloqueado"
        verbose_name_plural = "Usuarios Bloqueados"
        ordering = ['-fecha_bloqueo']
    
    def __str__(self):
        return f"{self.username} - Bloqueado por {self.bloqueado_por}"
    
    @classmethod
    def esta_bloqueado(cls, username, ip=None):
        """Verificar si un usuario o IP está bloqueado"""
        from django.utils import timezone
        
        # Buscar bloqueo por username
        bloqueo = cls.objects.filter(
            username=username,
            activo=True
        ).filter(
            models.Q(fecha_expiracion__isnull=True) | 
            models.Q(fecha_expiracion__gt=timezone.now())
        ).first()
        
        if bloqueo:
            return True, bloqueo.razon
        
        # Buscar bloqueo por IP si se proporciona
        if ip:
            bloqueo_ip = cls.objects.filter(
                ip_address=ip,
                activo=True
            ).filter(
                models.Q(fecha_expiracion__isnull=True) | 
                models.Q(fecha_expiracion__gt=timezone.now())
            ).first()
            
            if bloqueo_ip:
                return True, bloqueo_ip.razon
        
        return False, None
    """Modelo para registrar acciones de moderación"""
    TIPO_ACCIONES = [
        ('bloqueo', 'Bloqueo de Usuario'),
        ('desbloqueo', 'Desbloqueo de Usuario'),
        ('advertencia', 'Advertencia'),
        ('eliminacion', 'Eliminación de Mensaje'),
        ('desbloqueo_manual', 'Desbloqueo Manual'),
    ]
    
    tipo_accion = models.CharField(max_length=20, choices=TIPO_ACCIONES)
    username_objetivo = models.CharField(max_length=150, help_text="Usuario afectado por la acción")
    moderador = models.CharField(max_length=150, help_text="Usuario admin que realizó la acción")
    mensaje_id = models.IntegerField(null=True, blank=True, help_text="ID del mensaje eliminado (si aplica)")
    contenido_mensaje = models.TextField(blank=True, help_text="Contenido del mensaje eliminado (si aplica)")
    razon = models.TextField(blank=True, help_text="Razón de la acción")
    fecha_accion = models.DateTimeField(auto_now_add=True)
    ip_moderador = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Acción de Moderación"
        verbose_name_plural = "Acciones de Moderación"
        ordering = ['-fecha_accion']
    
    def __str__(self):
        return f"{self.get_tipo_accion_display()} - {self.username_objetivo} por {self.moderador}"
