from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from apps.radio.models import OyenteActivo
from apps.users.models import User


@staff_member_required
def ver_usuarios(request):
    """Ver lista de usuarios registrados"""
    usuarios = User.objects.all().order_by('-date_joined')
    
    # Estadísticas
    total_usuarios = usuarios.count()
    usuarios_activos_mes = User.objects.filter(
        date_joined__gte=timezone.now() - timezone.timedelta(days=30)
    ).count()
    usuarios_staff = User.objects.filter(is_staff=True).count()
    usuarios_activos = User.objects.filter(is_active=True).count()
    
    context = {
        'usuarios': usuarios,
        'total_usuarios': total_usuarios,
        'usuarios_activos_mes': usuarios_activos_mes,
        'usuarios_staff': usuarios_staff,
        'usuarios_activos': usuarios_activos,
        'page_title': 'Gestión de Usuarios'
    }
    
    return render(request, 'dashboard/usuarios.html', context)


@staff_member_required
def detalle_usuario(request, user_id):
    """Ver detalles de un usuario específico"""
    usuario = get_object_or_404(User, id=user_id)
    
    # Estadísticas del usuario
    conexiones_usuario = OyenteActivo.objects.filter(
        ip_address__contains=usuario.email.split('@')[0]  # Búsqueda aproximada
    ).count()
    
    context = {
        'usuario': usuario,
        'conexiones_usuario': conexiones_usuario,
        'page_title': f'Detalles de {usuario.username}'
    }
    
    return render(request, 'dashboard/detalle_usuario.html', context)


@staff_member_required
def toggle_usuario_staff(request, user_id):
    """Activar/desactivar permisos de staff"""
    if request.method == 'POST':
        usuario = get_object_or_404(User, id=user_id)
        usuario.is_staff = not usuario.is_staff
        usuario.save()
        
        estado = 'activados' if usuario.is_staff else 'desactivados'
        messages.success(request, f'Permisos de staff {estado} para {usuario.username}')
    
    return redirect('dashboard:ver_usuarios')


@staff_member_required
def toggle_usuario_activo(request, user_id):
    """Activar/desactivar usuario"""
    if request.method == 'POST':
        usuario = get_object_or_404(User, id=user_id)
        usuario.is_active = not usuario.is_active
        usuario.save()
        
        estado = 'activado' if usuario.is_active else 'desactivado'
        messages.success(request, f'Usuario {usuario.username} {estado}')
    
    return redirect('dashboard:ver_usuarios')
