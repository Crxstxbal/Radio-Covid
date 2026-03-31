import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'radio_web.settings')
django.setup()

from apps.radio.models import EstacionRadio

def crear_estacion():
    # Eliminar estaciones existentes
    EstacionRadio.objects.all().delete()
    
    # Crear nueva estación
    estacion = EstacionRadio.objects.create(
        nombre="Radio Web Online",
        descripcion="La mejor música 24/7 - Streaming en vivo",
        stream_url="https://sonic-us.fhost.cl/8126/stream",
        activa=True
    )
    
    print(f"✅ Estación creada: {estacion.nombre}")
    print(f"📡 URL Streaming: {estacion.stream_url}")
    print(f"🎯 Activa: {estacion.activa}")
    
    return estacion

if __name__ == "__main__":
    crear_estacion()
