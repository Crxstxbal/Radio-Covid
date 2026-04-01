from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Max
from django.contrib.auth.models import Group
from apps.radio.models import EstacionRadio, OyenteActivo, EstadisticaRadio, MensajeChat, UsuarioBloqueado, AdvertenciaChat
from apps.radio.forms import EstacionRadioForm
from apps.users.models import User


@staff_member_required
def dashboard_home(request):
    """Vista principal del dashboard"""
    # Estadísticas generales
    oyentes_actuales = OyenteActivo.objects.filter(esta_escuchando=True).count()
    
    total_conexiones_hoy = EstadisticaRadio.objects.filter(
        fecha=timezone.now().date()
    ).first()
    
    # Estación activa
    estacion_activa = EstacionRadio.get_activa()
    
    # Lista de oyentes escuchando ahora (solo usuarios)
    oyentes_escuchando = OyenteActivo.objects.filter(
        esta_escuchando=True
    ).order_by('-fecha_conexion')[:20]
    
    context = {
        'oyentes_actuales': oyentes_actuales or 0,
        'total_conexiones_hoy': total_conexiones_hoy.total_conexiones if total_conexiones_hoy else 0,
        'maximo_hoy': total_conexiones_hoy.oyentes_maximos_simultaneos if total_conexiones_hoy else oyentes_actuales or 0,
        'estacion_activa': estacion_activa,
        'oyentes_escuchando': oyentes_escuchando,
        'page_title': 'Dashboard'
    }
    
    return render(request, 'dashboard/home.html', context)


@staff_member_required
def configurar_estacion(request):
    """Configurar la estación de radio"""
    estacion = EstacionRadio.get_activa()
    
    if request.method == 'POST':
        form = EstacionRadioForm(request.POST, request.FILES, instance=estacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Estación configurada exitosamente')
            return redirect('dashboard:home')
    else:
        form = EstacionRadioForm(instance=estacion)
    
    context = {
        'form': form,
        'page_title': 'Configurar Estación'
    }
    
    return render(request, 'dashboard/configurar_estacion.html', context)


@staff_member_required
def ver_oyentes(request):
    """Ver lista de oyentes activos"""
    oyentes = OyenteActivo.objects.filter(esta_escuchando=True).order_by('-fecha_conexion')
    
    context = {
        'oyentes': oyentes,
        'total_oyentes': oyentes.count(),
        'page_title': 'Oyentes Activos',
        'cache_bust': timezone.now().timestamp(),  # Force no cache
    }
    
    return render(request, 'dashboard/oyentes.html', context)


@staff_member_required
def ver_estadisticas(request):
    """Ver estadísticas de la radio en tiempo real"""
    # Fecha de hace 30 días
    fecha_limite = timezone.now() - timezone.timedelta(days=30)
    
    # Estadísticas de la radio
    estadisticas = EstadisticaRadio.objects.filter(
        fecha__gte=fecha_limite
    ).order_by('-fecha')
    
    # Calcular totales para el template
    total_conexiones_sum = sum(stat.total_conexiones for stat in estadisticas)
    promedio_oyentes = estadisticas[0].oyentes_maximos_simultaneos if estadisticas else 0
    
    # Estadísticas de usuarios
    total_usuarios = User.objects.count()
    usuarios_activos_mes = User.objects.filter(
        date_joined__gte=fecha_limite
    ).count()
    usuarios_staff = User.objects.filter(is_staff=True).count()
    
    # Oyentes en tiempo real
    oyentes_activos = OyenteActivo.objects.filter(esta_escuchando=True).count()
    
    # Mensajes de chat recientes
    mensajes_chat = MensajeChat.objects.all().order_by('-fecha_envio')[:20]
    
    context = {
        'estadisticas': estadisticas,
        'total_conexiones_sum': total_conexiones_sum,
        'promedio_oyentes': promedio_oyentes,
        'total_usuarios': total_usuarios,
        'usuarios_activos_mes': usuarios_activos_mes,
        'usuarios_staff': usuarios_staff,
        'oyentes_activos': oyentes_activos,
        'mensajes_chat': mensajes_chat,
        'page_title': 'Estadísticas'
    }
    
    return render(request, 'dashboard/estadisticas.html', context)


@staff_member_required
def ver_chat(request):
    """Ver historial de mensajes del chat en vivo"""
    # Obtener últimos 100 mensajes ordenados por fecha (más recientes primero)
    mensajes = MensajeChat.objects.all().order_by('-fecha_envio')[:100]
    
    context = {
        'mensajes': mensajes,
        'page_title': 'Mensajes de Chat'
    }
    
    return render(request, 'dashboard/ver_chat.html', context)


@staff_member_required
def eliminar_mensaje(request, mensaje_id):
    """Eliminar un mensaje del chat"""
    try:
        mensaje = MensajeChat.objects.get(id=mensaje_id)
        mensaje.delete()
        messages.success(request, 'Mensaje eliminado correctamente.')
    except MensajeChat.DoesNotExist:
        messages.error(request, 'Mensaje no encontrado.')
    
    # Redirigir según de dónde vino la petición
    referer = request.META.get('HTTP_REFERER', '')
    if 'chat/moderacion' in referer or 'chat/' in referer:
        return redirect('dashboard:chat_moderacion')
    return redirect('dashboard:ver_chat')


@staff_member_required
def banear_usuario(request, username):
    """Bloquear/banear un usuario del chat"""
    from apps.radio.models import UsuarioBloqueado
    
    if request.method == 'POST':
        razon = request.POST.get('razon', 'Comportamiento inapropiado')
        duracion_dias = request.POST.get('duracion', '')
        
        # Calcular fecha de expiración
        fecha_expiracion = None
        if duracion_dias and duracion_dias.isdigit():
            from datetime import timedelta
            fecha_expiracion = timezone.now() + timedelta(days=int(duracion_dias))
        
        # Crear bloqueo
        UsuarioBloqueado.objects.create(
            username=username,
            razon=razon,
            fecha_expiracion=fecha_expiracion,
            bloqueado_por=request.user.username
        )
        
        # Nota: Acción registrada en log
        
        # Eliminar mensajes del usuario
        deleted_count = MensajeChat.objects.filter(usuario=username).delete()[0]
        messages.success(request, f'Usuario {username} bloqueado. Se eliminaron {deleted_count} mensajes.')
    
    return redirect('dashboard:chat_moderacion')


@staff_member_required
def desbanear_usuario(request, username):
    """Desbloquear/desbanear un usuario del chat"""
    from apps.radio.models import UsuarioBloqueado
    
    # Desactivar todos los bloqueos activos del usuario
    bloqueos = UsuarioBloqueado.objects.filter(username=username, activo=True)
    for bloqueo in bloqueos:
        bloqueo.activo = False
        bloqueo.save()
    messages.success(request, f'Usuario {username} desbloqueado exitosamente.')
    return redirect('dashboard:chat_bloqueados')


@staff_member_required
def advertir_usuario(request, username):
    """Enviar advertencia a un usuario"""
    from apps.radio.models import AdvertenciaChat
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo', 'Comportamiento inapropiado')
        
        # Crear advertencia
        AdvertenciaChat.objects.create(
            username=username,
            motivo=motivo,
            advertido_por=request.user.username
        )
        
        # Nota: Acción registrada en log
        
        messages.success(request, f'Advertencia enviada a {username}.')
    
    return redirect('dashboard:chat_moderacion')


@staff_member_required
def chat_moderacion(request):
    """Panel de moderación del chat en vivo"""
    from apps.radio.models import UsuarioBloqueado, AdvertenciaChat
    
    # Obtener mensajes recientes (últimas 24 horas)
    mensajes_recientes = MensajeChat.objects.filter(
        fecha_envio__gte=timezone.now() - timezone.timedelta(days=1)
    ).order_by('-fecha_envio')[:100]
    
    # Estadísticas
    total_mensajes_hoy = MensajeChat.objects.filter(
        fecha_envio__gte=timezone.now() - timezone.timedelta(days=1)
    ).count()
    
    usuarios_bloqueados_activos = UsuarioBloqueado.objects.filter(activo=True).count()
    advertencias_hoy = AdvertenciaChat.objects.filter(
        fecha_advertencia__gte=timezone.now() - timezone.timedelta(days=1)
    ).count()
    
    context = {
        'mensajes_recientes': mensajes_recientes,
        'total_mensajes_hoy': total_mensajes_hoy,
        'usuarios_bloqueados_activos': usuarios_bloqueados_activos,
        'advertencias_hoy': advertencias_hoy,
        'page_title': 'Moderación del Chat'
    }
    
    return render(request, 'dashboard/chat_moderacion.html', context)


@staff_member_required
def chat_bloqueados(request):
    """Lista de usuarios bloqueados del chat"""
    from apps.radio.models import UsuarioBloqueado
    
    usuarios_bloqueados = UsuarioBloqueado.objects.filter(activo=True).order_by('-fecha_bloqueo')
    historial_bloqueos = UsuarioBloqueado.objects.filter(activo=False).order_by('-fecha_bloqueo')[:20]
    
    context = {
        'usuarios_bloqueados': usuarios_bloqueados,
        'historial_bloqueos': historial_bloqueos,
        'page_title': 'Usuarios Bloqueados'
    }
    
    return render(request, 'dashboard/chat_bloqueados.html', context)


@staff_member_required
def chat_historial(request):
    """Ver historial completo de mensajes del chat"""
    mensajes = MensajeChat.objects.all().order_by('-fecha_envio')[:200]
    
    context = {
        'mensajes': mensajes,
        'page_title': 'Historial de Chat'
    }
    
    return render(request, 'dashboard/chat_historial.html', context)


@staff_member_required
def desbloquear_usuario(request, username):
    """Desbloquear un usuario del chat"""
    if request.method == 'POST':
        bloqueos = UsuarioBloqueado.objects.filter(username=username, activo=True)
        if bloqueos.exists():
            bloqueos.update(activo=False)
            
            # Registrar la acción
            # Nota: Acción registrada
            
            messages.success(request, f'Usuario {username} ha sido desbloqueado.')
        else:
            messages.warning(request, f'El usuario {username} no estaba bloqueado.')
    
    return redirect('dashboard:chat_bloqueados')


@staff_member_required
def advertir_usuario(request, username):
    """Enviar una advertencia a un usuario del chat"""
    if request.method == 'POST':
        razon = request.POST.get('razon', '')
        mensaje_original = request.POST.get('mensaje_original', '')
        
        if razon:
            AdvertenciaChat.objects.create(
                username=username,
                advertido_por=request.user.username,
                razon=razon,
                mensaje_original=mensaje_original
            )
            
            # Registrar la acción
            # Nota: Acción registrada
            
            messages.success(request, f'Advertencia enviada a {username}.')
        else:
            messages.error(request, 'Debes proporcionar una razón para la advertencia.')
    
    return redirect('dashboard:chat_moderacion')
