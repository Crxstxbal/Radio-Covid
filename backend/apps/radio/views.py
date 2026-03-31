from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Max
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import requests
import json
from .models import EstacionRadio, OyenteActivo, EstadisticaRadio, MensajeChat
from .serializers import (
    EstacionRadioSerializer, 
    OyenteActivoSerializer, 
    EstadisticaRadioSerializer,
    MensajeChatSerializer
)


class EstacionRadioViewSet(viewsets.ModelViewSet):
    """ViewSet para la estación de radio"""
    queryset = EstacionRadio.objects.all()
    serializer_class = EstacionRadioSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def activa(self, request):
        """Obtener la estación activa"""
        estacion = EstacionRadio.get_activa()
        if estacion:
            serializer = self.get_serializer(estacion)
            return Response(serializer.data)
        return Response({"error": "No hay estación activa"}, status=404)

    @action(detail=False, methods=['get'])
    def info_streaming(self, request):
        """Obtener información del streaming"""
        estacion = EstacionRadio.get_activa()
        if estacion:
            return Response({
                'nombre': estacion.nombre,
                'descripcion': estacion.descripcion,
                'stream_url': estacion.stream_url,
                'logo': estacion.logo.url if estacion.logo else None,
                'oyentes_conectados': OyenteActivo.obtener_conteo_actual()
            })
        return Response({"error": "No hay estación activa"}, status=404)


class OyenteActivoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de oyentes activos"""
    queryset = OyenteActivo.objects.all()
    serializer_class = OyenteActivoSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def registrar_conexion(self, request):
        """Registrar nueva conexión de oyente"""
        session_key = request.session.session_key or request.META.get('HTTP_X_SESSION_KEY', '')
        ip_address = request.META.get('REMOTE_ADDR', request.data.get('ip_address', ''))
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        if not session_key:
            return Response({"error": "Session key requerida"}, status=400)

        # Crear o actualizar oyente
        oyente, created = OyenteActivo.objects.get_or_create(
            session_key=session_key,
            defaults={
                'ip_address': ip_address,
                'user_agent': user_agent,
                'esta_escuchando': True
            }
        )

        if not created:
            oyente.ultima_actividad = timezone.now()
            oyente.esta_escuchando = True
            oyente.save()

        # Actualizar estadísticas
        self._actualizar_estadisticas()

        return Response({
            'message': 'Conexión registrada',
            'oyentes_conectados': OyenteActivo.obtener_conteo_actual()
        })

    @action(detail=False, methods=['post'])
    def actualizar_actividad(self, request):
        """Actualizar actividad de un oyente"""
        session_key = request.session.session_key or request.data.get('session_key', '')
        
        try:
            oyente = OyenteActivo.objects.get(session_key=session_key)
            oyente.ultima_actividad = timezone.now()
            oyente.esta_escuchando = True
            oyente.save()
            
            return Response({
                'message': 'Actividad actualizada',
                'oyentes_conectados': OyenteActivo.obtener_conteo_actual()
            })
        except OyenteActivo.DoesNotExist:
            return Response({"error": "Oyente no encontrado"}, status=404)

    @action(detail=False, methods=['post'])
    def desconexion(self, request):
        """Registrar desconexión de oyente"""
        session_key = request.session.session_key or request.data.get('session_key', '')
        
        try:
            oyente = OyenteActivo.objects.get(session_key=session_key)
            oyente.esta_escuchando = False
            oyente.save()
            
            return Response({
                'message': 'Desconexión registrada',
                'oyentes_conectados': OyenteActivo.obtener_conteo_actual()
            })
        except OyenteActivo.DoesNotExist:
            return Response({"error": "Oyente no encontrado"}, status=404)

    @action(detail=False, methods=['get', 'post'])
    def conteo_actual(self, request):
        """Obtener conteo actual de oyentes activos"""
        if request.method == 'POST':
            return self._registrar_conteo(request)
        else:
            # GET request - solo devolver conteo sin registrar
            count = OyenteActivo.objects.filter(esta_escuchando=True).count()
            return Response({
                'conteo': count,
                'timestamp': timezone.now().isoformat()
            })

    def _actualizar_estadisticas(self):
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


class EstadisticaRadioViewSet(viewsets.ModelViewSet):
    """ViewSet para estadísticas de radio"""
    queryset = EstadisticaRadio.objects.all()
    serializer_class = EstadisticaRadioSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def recientes(self, request):
        """Obtener estadísticas recientes"""
        from datetime import timedelta
        fecha_limite = timezone.now().date() - timedelta(days=7)
        estadisticas = self.queryset.filter(fecha__gte=fecha_limite)
        serializer = self.get_serializer(estadisticas, many=True)
        return Response(serializer.data)


def streaming_proxy(request):
    """Proxy para el streaming de radio para evitar CORS"""
    try:
        # Obtener la estación activa
        estacion = EstacionRadio.get_activa()
        if not estacion or not estacion.stream_url:
            return HttpResponse("No hay URL de streaming configurada", status=404)
        
        # Hacer la petición al servidor de streaming
        response = requests.get(
            estacion.stream_url,
            stream=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (compatible; RadioProxy/1.0)',
                'Accept': '*/*',
                'Accept-Encoding': 'identity',
                'Range': request.META.get('HTTP_RANGE', ''),
            }
        )
        
        # Crear respuesta streaming
        streaming_response = StreamingHttpResponse(
            response.iter_content(chunk_size=8192),
            content_type=response.headers.get('Content-Type', 'audio/mpeg')
        )
        
        # Copiar headers importantes
        for header, value in response.headers.items():
            if header.lower() in ['content-type', 'content-length', 'accept-ranges', 'content-range']:
                streaming_response[header] = value
        
        # Agregar headers CORS
        streaming_response['Access-Control-Allow-Origin'] = '*'
        streaming_response['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
        streaming_response['Access-Control-Allow-Headers'] = 'Range'
        
        return streaming_response
        
    except Exception as e:
        return HttpResponse(f"Error en el proxy de streaming: {str(e)}", status=500)


# ─── API para Chat en Vivo ─────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def api_chat_mensajes(request):
    """
    API para obtener historial de mensajes y enviar nuevos mensajes
    GET: Obtener últimos 50 mensajes
    POST: Enviar nuevo mensaje
    """
    if request.method == 'GET':
        # Obtener últimos 50 mensajes ordenados por fecha (más recientes primero)
        mensajes = MensajeChat.objects.all().order_by('-fecha_envio')[:50]
        # Invertir para mostrar cronológicamente (más antiguos primero en el chat)
        mensajes_list = list(mensajes)[::-1]
        
        data = {
            'success': True,
            'mensajes': [msg.to_dict() for msg in mensajes_list],
            'total': len(mensajes_list)
        }
        return Response(data)
    
    elif request.method == 'POST':
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body)
            usuario = data.get('usuario', '').strip()
            mensaje_texto = data.get('mensaje', '').strip()
            
            # Validaciones
            if not usuario:
                return Response({
                    'success': False,
                    'error': 'El nombre de usuario es requerido'
                }, status=400)
            
            if not mensaje_texto:
                return Response({
                    'success': False,
                    'error': 'El mensaje no puede estar vacío'
                }, status=400)
            
            if len(mensaje_texto) > 500:
                return Response({
                    'success': False,
                    'error': 'El mensaje no puede exceder 500 caracteres'
                }, status=400)
            
            # Crear el mensaje
            ip_address = request.META.get('REMOTE_ADDR')
            mensaje = MensajeChat.objects.create(
                usuario=usuario,
                mensaje=mensaje_texto,
                ip_address=ip_address
            )
            
            return Response({
                'success': True,
                'mensaje': mensaje.to_dict()
            }, status=201)
            
        except json.JSONDecodeError:
            return Response({
                'success': False,
                'error': 'Formato JSON inválido'
            }, status=400)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_chat_usuarios_online(request):
    """
    Obtener cantidad de usuarios en línea (conectados al WebSocket)
    """
    # Este valor se actualizará desde el WebSocket consumer
    # Por ahora devolvemos un valor estimado basado en oyentes activos
    oyentes_count = OyenteActivo.objects.filter(esta_escuchando=True).count()
    
    return Response({
        'success': True,
        'usuarios_online': oyentes_count,
        'timestamp': timezone.now().isoformat()
    })


# ─── API para Moderación de Chat ──────────────────────────────────────────

from .models import UsuarioBloqueado, AdvertenciaChat


@api_view(['DELETE'])
@permission_classes([AllowAny])
def api_chat_eliminar_mensaje(request, mensaje_id):
    """
    Eliminar un mensaje del chat (solo moderadores)
    """
    try:
        moderador = request.data.get('moderador', '').strip()
        razon = request.data.get('razon', '').strip()
        
        if not moderador:
            return Response({
                'success': False,
                'error': 'Se requiere identificación del moderador'
            }, status=400)
        
        # Obtener el mensaje
        mensaje = MensajeChat.objects.get(id=mensaje_id)
        contenido_original = mensaje.mensaje
        username_objetivo = mensaje.usuario
        
        # Nota: Acción de eliminación registrada (sin ModeracionChat model)
        print(f"[MODERACIÓN] {moderador} eliminó mensaje de {username_objetivo}")
        
        # Eliminar el mensaje
        mensaje.delete()
        
        return Response({
            'success': True,
            'message': 'Mensaje eliminado correctamente',
            'mensaje_id': mensaje_id,
            'eliminado_por': moderador
        })
        
    except MensajeChat.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Mensaje no encontrado'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_chat_bloquear_usuario(request):
    """
    Bloquear un usuario del chat
    """
    try:
        username = request.data.get('username', '').strip()
        moderador = request.data.get('moderador', '').strip()
        razon = request.data.get('razon', '').strip()
        permanente = request.data.get('permanente', True)
        duracion_horas = request.data.get('duracion_horas', None)
        
        if not username or not moderador:
            return Response({
                'success': False,
                'error': 'Se requiere username del usuario y moderador'
            }, status=400)
        
        # Calcular fecha de desbloqueo si es temporal
        fecha_desbloqueo = None
        if not permanente and duracion_horas:
            from datetime import timedelta
            fecha_desbloqueo = timezone.now() + timedelta(hours=int(duracion_horas))
        
        # Crear o actualizar bloqueo
        bloqueo, created = UsuarioBloqueado.objects.update_or_create(
            username=username,
            defaults={
                'bloqueado_por': moderador,
                'razon': razon,
                'permanente': permanente,
                'fecha_desbloqueo': fecha_desbloqueo,
                'activo': True
            }
        )
        
        # Nota: Acción de bloqueo registrada (sin ModeracionChat model)
        print(f"[MODERACIÓN] {moderador} bloqueó a {username}")
        
        return Response({
            'success': True,
            'message': f'Usuario {username} bloqueado correctamente',
            'bloqueo': {
                'username': username,
                'permanente': permanente,
                'fecha_desbloqueo': fecha_desbloqueo.isoformat() if fecha_desbloqueo else None
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_chat_desbloquear_usuario(request):
    """
    Desbloquear un usuario del chat
    """
    try:
        username = request.data.get('username', '').strip()
        moderador = request.data.get('moderador', '').strip()
        razon = request.data.get('razon', '').strip()
        
        if not username or not moderador:
            return Response({
                'success': False,
                'error': 'Se requiere username del usuario y moderador'
            }, status=400)
        
        # Buscar y desactivar bloqueos activos
        bloqueos = UsuarioBloqueado.objects.filter(username=username, activo=True)
        if bloqueos.exists():
            bloqueos.update(activo=False)
        
        # Nota: Acción de desbloqueo registrada (sin ModeracionChat model)
        print(f"[MODERACIÓN] {moderador} desbloqueó a {username}")
        
        return Response({
            'success': True,
            'message': f'Usuario {username} desbloqueado correctamente'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_chat_advertir_usuario(request):
    """
    Enviar una advertencia a un usuario del chat
    """
    try:
        username = request.data.get('username', '').strip()
        moderador = request.data.get('moderador', '').strip()
        razon = request.data.get('razon', '').strip()
        mensaje_original = request.data.get('mensaje_original', '').strip()
        
        if not username or not moderador or not razon:
            return Response({
                'success': False,
                'error': 'Se requiere username, moderador y razón de la advertencia'
            }, status=400)
        
        # Crear la advertencia
        advertencia = AdvertenciaChat.objects.create(
            username=username,
            advertido_por=moderador,
            razon=razon,
            mensaje_original=mensaje_original
        )
        
        # Nota: Acción de advertencia registrada (sin ModeracionChat model)
        print(f"[MODERACIÓN] {moderador} advirtió a {username}")
        
        return Response({
            'success': True,
            'message': f'Advertencia enviada a {username}',
            'advertencia': {
                'id': advertencia.id,
                'username': username,
                'razon': razon,
                'fecha': advertencia.fecha_advertencia.isoformat()
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_chat_verificar_bloqueo(request, username):
    """
    Verificar si un usuario está bloqueado del chat
    """
    try:
        esta_bloqueado, _ = UsuarioBloqueado.esta_bloqueado(username)
        
        bloqueo_info = None
        if esta_bloqueado:
            bloqueo = UsuarioBloqueado.objects.filter(
                username=username,
                activo=True
            ).first()
            if bloqueo:
                bloqueo_info = {
                    'razon': bloqueo.razon,
                    'fecha_bloqueo': bloqueo.fecha_bloqueo.isoformat(),
                    'permanente': bloqueo.permanente,
                    'fecha_desbloqueo': bloqueo.fecha_desbloqueo.isoformat() if bloqueo.fecha_desbloqueo else None
                }
        
        return Response({
            'success': True,
            'bloqueado': esta_bloqueado,
            'bloqueo_info': bloqueo_info
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_chat_lista_bloqueados(request):
    """
    Obtener lista de usuarios bloqueados del chat
    """
    try:
        bloqueados = UsuarioBloqueado.objects.filter(activo=True).order_by('-fecha_bloqueo')
        
        data = []
        for bloqueo in bloqueados:
            data.append({
                'username': bloqueo.username,
                'bloqueado_por': bloqueo.bloqueado_por,
                'razon': bloqueo.razon,
                'fecha_bloqueo': bloqueo.fecha_bloqueo.isoformat(),
                'permanente': bloqueo.permanente,
                'fecha_desbloqueo': bloqueo.fecha_desbloqueo.isoformat() if bloqueo.fecha_desbloqueo else None
            })
        
        return Response({
            'success': True,
            'bloqueados': data,
            'total': len(data)
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_chat_advertencias_usuario(request, username):
    """
    Obtener advertencias de un usuario específico
    """
    try:
        advertencias = AdvertenciaChat.objects.filter(username=username).order_by('-fecha_advertencia')
        
        # Marcar como leídas si se solicita
        if request.query_params.get('marcar_leidas') == 'true':
            advertencias.filter(leida=False).update(leida=True)
        
        data = []
        for adv in advertencias:
            data.append({
                'id': adv.id,
                'razon': adv.razon,
                'mensaje_original': adv.mensaje_original,
                'advertido_por': adv.advertido_por,
                'fecha_advertencia': adv.fecha_advertencia.isoformat(),
                'leida': adv.leida
            })
        
        return Response({
            'success': True,
            'username': username,
            'advertencias': data,
            'total': len(data),
            'no_leidas': sum(1 for a in data if not a['leida'])
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
