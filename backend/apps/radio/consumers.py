import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import OyenteActivo, EstadisticaRadio, MensajeChat, UsuarioBloqueado, AdvertenciaChat


class RadioConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Manejar conexión WebSocket"""
        # El tab_id se recibirá más tarde del cliente, por ahora usar IP
        self.tab_id = None
        
        # Aceptar conexión
        await self.accept()
        
        # Registrar oyente inicialmente con IP (se actualizará cuando reciba tab_id)
        await self.registrar_oyente()
        
        # Unirse al grupo de radio
        await self.channel_layer.group_add(
            "radio_listeners",
            self.channel_name
        )
        
        # Enviar conteo actual
        await self.enviar_conteo_actual()
        
        # Iniciar keepalive para mantener conexión activa (evita desconexiones de Render)
        self.keepalive_task = asyncio.create_task(self.keepalive_loop())

    async def keepalive_loop(self):
        """Enviar ping cada 30 segundos para mantener conexión activa"""
        try:
            while True:
                await asyncio.sleep(30)  # Ping cada 30 segundos
                await self.send(text_data=json.dumps({
                    'type': 'keepalive',
                    'timestamp': timezone.now().isoformat()
                }))
        except asyncio.CancelledError:
            # La conexión se cerró, terminar el loop
            pass
        except Exception as e:
            print(f"Error en keepalive: {e}")
            return  # Salir del método si hay error

    async def disconnect(self, close_code):
        """Manejar desconexión WebSocket"""
        # Cancelar keepalive task
        if hasattr(self, 'keepalive_task'):
            self.keepalive_task.cancel()
            try:
                await self.keepalive_task
            except asyncio.CancelledError:
                pass
        
        # Marcar como no escuchando
        """Manejar desconexión WebSocket"""
        # Marcar como no escuchando
        await self.desregistrar_oyente()
        
        # Salir del grupo
        await self.channel_layer.group_discard(
            "radio_listeners",
            self.channel_name
        )
        
        # Enviar conteo actual a todos
        await self.channel_layer.group_send(
            "radio_listeners",
            {
                'type': 'actualizar_conteo',
                'message': {'oyentes_conectados': await self.obtener_conteo()}
            }
        )

    async def receive(self, text_data):
        """Manejar mensajes recibidos"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'heartbeat':
                # Actualizar actividad del oyente
                await self.actualizar_actividad()
                await self.enviar_conteo_actual()
            elif message_type == 'identificar':
                # Recibir tab_id y nombre de usuario
                usuario = data.get('usuario')
                tab_id = data.get('tab_id')
                
                if tab_id:
                    self.tab_id = tab_id
                    print(f"Tab ID recibido: {tab_id}")
                    # Migrar oyente de IP a tab_id
                    await self.migrar_oyente_a_tab_id(tab_id, usuario)
                elif usuario:
                    await self.actualizar_usuario(usuario)
                    print(f"Usuario identificado: {usuario}")
                
        except json.JSONDecodeError:
            pass

    @database_sync_to_async
    def migrar_oyente_a_tab_id(self, tab_id, usuario=None):
        """Migrar oyente de IP a tab_id cuando se recibe"""
        try:
            ip_address = self.get_client_ip()
            old_session_key = f"ip_{ip_address}"
            
            # Primero verificar si ya existe un oyente con este tab_id
            try:
                existing = OyenteActivo.objects.get(session_key=tab_id)
                # Ya existe, solo actualizar usuario si es necesario
                if usuario and usuario != existing.usuario:
                    existing.usuario = usuario
                    existing.save(update_fields=['usuario'])
                print(f"Oyente con tab_id {tab_id} ya existe, actualizado")
                return
            except OyenteActivo.DoesNotExist:
                pass
            
            # Buscar oyente por IP y migrar
            try:
                oyente = OyenteActivo.objects.get(session_key=old_session_key)
                # Actualizar a usar tab_id
                oyente.session_key = tab_id
                if usuario:
                    oyente.usuario = usuario
                oyente.save()
                print(f"Oyente migrado de {old_session_key} a {tab_id}")
            except OyenteActivo.DoesNotExist:
                # No existe, crear nuevo con tab_id
                OyenteActivo.objects.create(
                    session_key=tab_id,
                    ip_address=ip_address,
                    usuario=usuario or 'Anónimo',
                    esta_escuchando=True
                )
                print(f"Nuevo oyente creado con tab_id: {tab_id}")
        except Exception as e:
            print(f"Error migrando oyente: {e}")

    @database_sync_to_async
    def actualizar_usuario(self, usuario):
        """Actualizar el nombre de usuario del oyente - usa tab_id si está disponible"""
        try:
            ip_address = self.get_client_ip()
            
            # Usar tab_id si está disponible, sino IP
            if self.tab_id:
                session_key = self.tab_id
            else:
                session_key = f"ip_{ip_address}"
            
            oyente = OyenteActivo.objects.get(session_key=session_key)
            oyente.usuario = usuario
            oyente.save(update_fields=['usuario'])
            print(f"Usuario {usuario} guardado para session {session_key}")
        except OyenteActivo.DoesNotExist:
            print(f"No se encontró oyente con session_key {session_key}")
            pass

    async def actualizar_conteo(self, event):
        """Enviar conteo actualizado a todos los oyentes"""
        await self.send(text_data=json.dumps({
            'type': 'conteo_actualizado',
            'oyentes_conectados': event['message']['oyentes_conectados']
        }))

    @database_sync_to_async
    def registrar_oyente(self):
        """Registrar nuevo oyente en la base de datos - usa tab_id si está disponible"""
        ip_address = self.get_client_ip()
        
        # Usar tab_id si está disponible, sino IP
        if self.tab_id:
            session_key = self.tab_id
        else:
            session_key = f"ip_{ip_address}"
        
        # Headers es una lista de tuplas en ASGI
        headers_list = self.scope.get('headers', [])
        headers = {}
        for name, value in headers_list:
            headers[name.lower()] = value
        
        user_agent = headers.get(b'user-agent', b'').decode('utf-8')[:100]
        
        # Obtener usuario autenticado si existe
        usuario = None
        if 'user' in self.scope and self.scope['user'] and not self.scope['user'].is_anonymous:
            usuario = self.scope['user'].username
        
        try:
            # Intentar obtener existente
            oyente = OyenteActivo.objects.get(session_key=session_key)
            # Actualizar existente
            oyente.ultima_actividad = timezone.now()
            oyente.esta_escuchando = True
            oyente.user_agent = user_agent
            oyente.ip_address = ip_address
            if usuario:
                oyente.usuario = usuario
            oyente.save()
        except OyenteActivo.DoesNotExist:
            # Crear nuevo
            OyenteActivo.objects.create(
                session_key=session_key,
                ip_address=ip_address,
                user_agent=user_agent,
                usuario=usuario or 'Anónimo',
                esta_escuchando=True
            )
        
        # Actualizar estadísticas
        self.actualizar_estadisticas()

    @database_sync_to_async
    def desregistrar_oyente(self):
        """Marcar oyente como desconectado - usa tab_id si está disponible"""
        ip_address = self.get_client_ip()
        
        # Usar tab_id si está disponible, sino IP
        if self.tab_id:
            session_key = self.tab_id
        else:
            session_key = f"ip_{ip_address}"
        
        try:
            oyente = OyenteActivo.objects.get(session_key=session_key)
            oyente.esta_escuchando = False
            oyente.save()
        except OyenteActivo.DoesNotExist:
            pass

    @database_sync_to_async
    def actualizar_actividad(self):
        """Actualizar actividad del oyente - usa tab_id si está disponible"""
        ip_address = self.get_client_ip()
        
        # Usar tab_id si está disponible, sino IP
        if self.tab_id:
            session_key = self.tab_id
        else:
            session_key = f"ip_{ip_address}"
        
        try:
            oyente = OyenteActivo.objects.get(session_key=session_key)
            oyente.ultima_actividad = timezone.now()
            oyente.esta_escuchando = True
            oyente.save()
        except OyenteActivo.DoesNotExist:
            pass

    @database_sync_to_async
    def obtener_conteo(self):
        """Obtener conteo actual de oyentes"""
        return OyenteActivo.obtener_conteo_actual()

    async def enviar_conteo_actual(self):
        """Enviar conteo actual al cliente"""
        conteo = await self.obtener_conteo()
        await self.send(text_data=json.dumps({
            'type': 'conteo_actualizado',
            'oyentes_conectados': conteo
        }))

    def get_client_ip(self):
        """Obtener IP del cliente"""
        # Headers es una lista de tuplas en ASGI: [(b'name', b'value'), ...]
        headers_list = self.scope.get('headers', [])
        headers = {}
        for name, value in headers_list:
            headers[name.lower()] = value
        
        x_forwarded_for = headers.get(b'x-forwarded-for')
        if x_forwarded_for:
            ip = x_forwarded_for.decode('utf-8').split(',')[0]
        else:
            client = self.scope.get('client')
            if client:
                ip = client[0] if isinstance(client, (list, tuple)) else client
            else:
                ip = '127.0.0.1'
        return ip

    def generate_session_key(self):
        """Generar clave de sesión única"""
        import uuid
        return str(uuid.uuid4())

    def actualizar_estadisticas(self):
        """Actualizar estadísticas diarias"""
        hoy = timezone.now().date()
        estadistica, created = EstadisticaRadio.objects.get_or_create(
            fecha=hoy,
            defaults={
                'oyentes_maximos_simultaneos': OyenteActivo.obtener_conteo_actual(),
                'total_conexiones': 1
            }
        )

        if not created:
            # Actualizar máximo si es necesario
            conteo_actual = OyenteActivo.obtener_conteo_actual()
            if conteo_actual > estadistica.oyentes_maximos_simultaneos:
                estadistica.oyentes_maximos_simultaneos = conteo_actual
            
            # Incrementar total de conexiones
            estadistica.total_conexiones += 1
            estadistica.save()


class ChatConsumer(AsyncWebsocketConsumer):
    """Consumer WebSocket para chat en vivo"""
    
    async def connect(self):
        """Cuando un cliente se conecta al WebSocket"""
        self.room_group_name = 'radio_chat'
        
        # Unirse al grupo de chat
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Aceptar conexión
        await self.accept()
        
        # Enviar historial de mensajes
        historial = await self.get_historial_mensajes()
        await self.send(text_data=json.dumps({
            'type': 'historial_mensajes',
            'mensajes': historial
        }))
        
        # Obtener y enviar conteo de usuarios conectados
        count = await self.get_chat_user_count()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'usuarios_conectados',
                'cantidad': count
            }
        )
    
    async def disconnect(self, close_code):
        """Cuando un cliente se desconecta del WebSocket"""
        # Salir del grupo de chat
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Enviar conteo actualizado a todos los usuarios
        count = await self.get_chat_user_count()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'usuarios_conectados',
                'cantidad': count
            }
        )
    
    async def receive(self, text_data):
        """Cuando se recibe un mensaje del cliente"""
        try:
            data = json.loads(text_data)
            mensaje_tipo = data.get('type', 'mensaje_chat')
            
            if mensaje_tipo == 'mensaje_chat':
                usuario = data.get('usuario', '').strip()
                mensaje_texto = data.get('mensaje', '').strip()
                temp_id = data.get('id')  # ID temporal del cliente
                
                # Validaciones
                if not usuario or not mensaje_texto:
                    return
                
                if len(mensaje_texto) > 500:
                    mensaje_texto = mensaje_texto[:500]
                
                # Verificar si el usuario está bloqueado
                esta_bloqueado, razon_bloqueo = await self.verificar_usuario_bloqueado(usuario)
                if esta_bloqueado:
                    await self.send(text_data=json.dumps({
                        'type': 'error_chat',
                        'error': 'Tu cuenta ha sido bloqueada del chat. Contacta a un administrador.'
                    }))
                    return
                
                # Verificar advertencias pendientes
                advertencias = await self.obtener_advertencias_pendientes(usuario)
                
                # Guardar mensaje en base de datos
                mensaje_guardado = await self.guardar_mensaje(
                    usuario, mensaje_texto
                )
                
                # Enviar confirmación al remitente con el ID real
                await self.send(text_data=json.dumps({
                    'type': 'mensaje_chat',
                    'id': mensaje_guardado['id'],
                    'temp_id': temp_id,
                    'usuario': usuario,
                    'mensaje': mensaje_texto,
                    'timestamp': mensaje_guardado['timestamp'],
                    'advertencias_usuario': advertencias
                }))
                
                # Enviar mensaje a los demás usuarios conectados (sin el remitente)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'mensaje_chat_broadcast',
                        'id': mensaje_guardado['id'],
                        'temp_id': temp_id,
                        'usuario': usuario,
                        'mensaje': mensaje_texto,
                        'timestamp': mensaje_guardado['timestamp'],
                        'advertencias_usuario': advertencias,
                        'sender_channel_name': self.channel_name  # Excluir al remitente
                    }
                )
                
            elif mensaje_tipo == 'notificacion_moderacion':
                # Reenviar notificación de moderación a todos
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'notificacion_moderacion',
                        'accion': data.get('accion'),
                        'username_objetivo': data.get('username_objetivo'),
                        'moderador': data.get('moderador'),
                        'razon': data.get('razon')
                    }
                )
                
        except json.JSONDecodeError:
            pass
        except Exception as e:
            print(f"Error en receive: {e}")
    
    async def mensaje_chat(self, event):
        """Envía un mensaje de chat al cliente WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'mensaje_chat',
            'id': event.get('id'),
            'usuario': event['usuario'],
            'mensaje': event['mensaje'],
            'timestamp': event['timestamp']
        }))
    
    async def mensaje_chat_broadcast(self, event):
        """Envía mensaje de chat a otros usuarios (excluye al remitente)"""
        # No enviar al remitente original
        if event.get('sender_channel_name') == self.channel_name:
            return
        
        await self.send(text_data=json.dumps({
            'type': 'mensaje_chat',
            'id': event['id'],
            'temp_id': event['temp_id'],
            'usuario': event['usuario'],
            'mensaje': event['mensaje'],
            'timestamp': event['timestamp'],
            'advertencias_usuario': event.get('advertencias_usuario', [])
        }))
    
    async def usuarios_conectados(self, event):
        """Envía actualización de usuarios conectados al cliente"""
        await self.send(text_data=json.dumps({
            'type': 'usuarios_conectados',
            'cantidad': event['cantidad']
        }))
    
    @database_sync_to_async
    def guardar_mensaje(self, usuario, mensaje_texto):
        """Guarda un mensaje en la base de datos"""
        try:
            mensaje = MensajeChat.objects.create(
                usuario=usuario,
                mensaje=mensaje_texto,
                ip_address=None
            )
            return {
                'id': mensaje.id,
                'timestamp': mensaje.fecha_envio.isoformat()
            }
        except Exception as e:
            print(f"Error guardando mensaje: {e}")
            return {
                'id': None,
                'timestamp': None
            }
    
    @database_sync_to_async
    def get_chat_user_count(self):
        """Obtener número de usuarios en el grupo de chat"""
        # Usar el conteo de oyentes activos como aproximación
        return OyenteActivo.obtener_conteo_actual()
    
    @database_sync_to_async
    def get_historial_mensajes(self, cantidad=50):
        """Obtiene los últimos mensajes del chat"""
        try:
            mensajes = MensajeChat.objects.all().order_by('-fecha_envio')[:cantidad]
            mensajes_list = list(mensajes)[::-1]
            
            return [
                {
                    'id': msg.id,
                    'usuario': msg.usuario,
                    'mensaje': msg.mensaje,
                    'timestamp': msg.fecha_envio.isoformat()
                }
                for msg in mensajes_list
            ]
        except Exception as e:
            print(f"Error obteniendo historial: {e}")
            return []
    
    @database_sync_to_async
    def verificar_usuario_bloqueado(self, username):
        """Verificar si un usuario está bloqueado del chat"""
        try:
            return UsuarioBloqueado.esta_bloqueado(username)
        except Exception as e:
            print(f"Error verificando bloqueo: {e}")
            return False
    
    @database_sync_to_async
    def obtener_advertencias_pendientes(self, username):
        """Obtener advertencias pendientes de un usuario"""
        try:
            advertencias = AdvertenciaChat.objects.filter(
                username=username,
                leida=False
            ).order_by('-fecha_advertencia')[:5]
            
            return [
                {
                    'id': adv.id,
                    'razon': adv.razon,
                    'advertido_por': adv.advertido_por,
                    'fecha': adv.fecha_advertencia.isoformat()
                }
                for adv in advertencias
            ]
        except Exception as e:
            print(f"Error obteniendo advertencias: {e}")
            return []
    
    async def notificacion_moderacion(self, event):
        """Envía una notificación de moderación al cliente"""
        await self.send(text_data=json.dumps({
            'type': 'notificacion_moderacion',
            'accion': event['accion'],
            'username_objetivo': event['username_objetivo'],
            'moderador': event['moderador'],
            'razon': event['razon']
        }))
