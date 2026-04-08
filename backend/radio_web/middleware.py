import time
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

class DatabasePingMiddleware(MiddlewareMixin):
    """
    Middleware que hace ping a la base de datos en cada request
    para mantener las conexiones vivas con el Supabase Pooler.
    """
    
    def process_request(self, request):
        # Solo hacer ping cada 60 segundos como máximo (no en cada request)
        current_time = time.time()
        last_ping = getattr(self, '_last_ping', 0)
        
        if current_time - last_ping > 60:  # Ping cada 60 segundos
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                self._last_ping = current_time
            except Exception:
                # Si falla, la conexión se reciclará automáticamente
                pass
        
        return None
