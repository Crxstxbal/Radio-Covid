from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from rest_framework import viewsets, permissions
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from django.conf import settings
from .models import User
from .forms import CustomUserCreationForm, UserLoginForm, UserProfileForm
from .serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer


# ViewSet para el router (mínimo necesario)
class UserViewSet(viewsets.ModelViewSet):
    """ViewSet para usuarios (básico)"""
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        # Retornamos None para evitar errores de serializer
        return None
    
    def list(self, request):
        """Lista de usuarios"""
        from rest_framework.response import Response
        from rest_framework import status
        return Response({"message": "UserViewSet working"}, status=status.HTTP_200_OK)


# Vistas API para el frontend (sin autenticación)
@csrf_exempt
@require_http_methods(["POST"])
def api_register(request):
    """API de registro para el frontend"""
    try:
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validaciones básicas
        if not username or not email or not password1 or not password2:
            return JsonResponse({'success': False, 'error': 'Todos los campos son requeridos'}, status=400)
        
        if password1 != password2:
            return JsonResponse({'success': False, 'error': 'Las contraseñas no coinciden'}, status=400)
        
        if len(password1) < 6:
            return JsonResponse({'success': False, 'error': 'La contraseña debe tener al menos 6 caracteres'}, status=400)
        
        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'error': 'El nombre de usuario ya existe'}, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'error': 'El email ya está registrado'}, status=400)
        
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        
        # Iniciar sesión automáticamente
        login(request, user)
        
        return JsonResponse({
            'success': True, 
            'message': 'Usuario creado exitosamente',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }, status=201)
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    """API de login para el frontend"""
    try:
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            return JsonResponse({'success': False, 'error': 'Usuario y contraseña son requeridos'}, status=400)
        
        user = authenticate(username=username, password=password)
        
        if user:
            login(request, user)
            return JsonResponse({
                'success': True, 
                'message': 'Login exitoso',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }, status=200)
        else:
            return JsonResponse({'success': False, 'error': 'Usuario o contraseña incorrectos'}, status=401)
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# Vistas de templates (para uso directo en Django)
def register_view(request):
    """Vista de registro"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, '¡Cuenta creada! Has iniciado sesión automáticamente.')
            
            # Iniciar sesión automáticamente
            login(request, user)
            
            return redirect('/')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """Vista de login"""
    form = UserLoginForm()
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            
            if user:
                login(request, user)
                return redirect('/')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'users/login.html', {'form': form})


@login_required
def profile_view(request):
    """Vista de perfil de usuario"""
    user = request.user
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Perfil actualizado correctamente!')
            return redirect('/')
    else:
        form = UserProfileForm(instance=user)
    
    return render(request, 'users/profile.html', {'form': form, 'user': user})


def logout_view(request):
    """Vista de logout"""
    logout(request)
    messages.success(request, '¡Sesión cerrada correctamente!')
    return redirect('/')


# Vistas para recuperación de contraseña (API)
@csrf_exempt
@require_http_methods(["POST"])
def api_password_reset_request(request):
    """
    Solicitar reseteo de contraseña. Envía un correo electrónico con el enlace de recuperación.
    Nota de seguridad: siempre retorna el mismo mensaje de éxito, independientemente de si el
    email existe o no, para prevenir user enumeration attacks.
    """
    import json
    from rest_framework import status
    from rest_framework.response import Response
    
    try:
        # Parsear JSON del body
        body = json.loads(request.body)
        serializer = PasswordResetRequestSerializer(data=body)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                # Generar token de reseteo
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Construir URL de reseteo (frontend)
                frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
                reset_url = f"{frontend_url}/reset-password/{uid}/{token}"
                
                # Enviar correo electrónico con diseño HTML
                subject = 'Recuperación de Contraseña - Radio Covid'
                
                # Mensaje en texto plano (fallback)
                plain_message = f"""Hola {user.first_name or user.username},

Recibimos una solicitud para restablecer tu contraseña.

Para crear una nueva contraseña, haz clic en el siguiente enlace:
{reset_url}

Este enlace expirará en 24 horas.

Si no solicitaste este cambio, puedes ignorar este correo electrónico y tu contraseña permanecerá sin cambios.

Saludos,
El equipo de Radio Covid"""
                
                # Mensaje HTML con diseño morado de Radio Covid
                html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recuperación de Contraseña - Radio Covid</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #4A0080 0%, #1A0033 50%, #0A000F 100%);">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table role="presentation" style="max-width: 600px; width: 100%; background: rgba(26,0,51,0.95); border-radius: 20px; border: 1px solid rgba(170,0,255,0.4); box-shadow: 0 0 60px rgba(170,0,255,0.3);">
                    <!-- Header -->
                    <tr>
                        <td style="padding: 50px 40px 30px; text-align: center; border-bottom: 1px solid rgba(170,0,255,0.3);">
                            <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #AA00FF 0%, #FF6D00 100%); border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 30px rgba(170,0,255,0.5);">
                                <span style="font-size: 40px;">🔐</span>
                            </div>
                            <h1 style="margin: 0; font-size: 28px; font-weight: 800; color: #F5F0FF; letter-spacing: 2px;">
                                RADIO COVID
                            </h1>
                            <p style="margin: 10px 0 0; font-size: 12px; color: #AA00FF; letter-spacing: 3px; text-transform: uppercase;">
                                Recuperación de Contraseña
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px;">
                            <p style="margin: 0 0 25px; font-size: 16px; color: #F5F0FF; line-height: 1.6;">
                                ¡Hola <strong style="color: #AA00FF;">{user.first_name or user.username}</strong>!
                            </p>
                            
                            <p style="margin: 0 0 25px; font-size: 15px; color: rgba(245,240,255,0.8); line-height: 1.6;">
                                Recibimos una solicitud para restablecer tu contraseña. Para crear una nueva, haz clic en el botón de abajo:
                            </p>
                            
                            <!-- Button -->
                            <table role="presentation" style="width: 100%; margin: 35px 0;">
                                <tr>
                                    <td align="center">
                                        <a href="{reset_url}" style="display: inline-block; padding: 18px 50px; background: linear-gradient(90deg, #AA00FF 0%, #FF6D00 100%); color: #ffffff; text-decoration: none; border-radius: 12px; font-size: 16px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; box-shadow: 0 4px 25px rgba(170,0,255,0.4);">
                                            Restablecer Contraseña →
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Info Box -->
                            <div style="padding: 25px; background: rgba(170,0,255,0.1); border-radius: 12px; border-left: 4px solid #AA00FF; margin: 30px 0;">
                                <h3 style="margin: 0 0 15px; color: #AA00FF; font-size: 16px; font-weight: 600;">
                                    ⚠️ Información Importante
                                </h3>
                                <ul style="margin: 0; padding-left: 20px; color: rgba(245,240,255,0.7); font-size: 14px; line-height: 1.8;">
                                    <li>El enlace expira en <strong style="color: #F5F0FF;">24 horas</strong></li>
                                    <li>Solo puedes usarlo <strong style="color: #F5F0FF;">una vez</strong></li>
                                    <li>Si no solicitaste esto, ignora este correo</li>
                                </ul>
                            </div>
                            
                            <p style="margin: 25px 0 15px; font-size: 13px; color: rgba(245,240,255,0.5); text-align: center;">
                                Si el botón no funciona, copia este enlace:
                            </p>
                            
                            <p style="margin: 0; padding: 15px; background: rgba(10,0,15,0.5); border-radius: 8px; font-size: 12px; color: #AA00FF; text-align: center; word-break: break-all; font-family: monospace;">
                                {reset_url}
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px 40px; text-align: center; border-top: 1px solid rgba(170,0,255,0.3); background: rgba(10,0,15,0.5);">
                            <p style="margin: 0 0 8px; font-size: 14px; color: #AA00FF; font-weight: 600;">
                                Radio Covid
                            </p>
                            <p style="margin: 0; font-size: 12px; color: rgba(245,240,255,0.4);">
                                © 2026 Todos los derechos reservados · La mejor música 24/7
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
                """
                
                try:
                    send_mail(
                        subject,
                        plain_message,
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                        html_message=html_message,
                    )
                except Exception:
                    # Fallar silenciosamente por seguridad
                    pass
                    
            except User.DoesNotExist:
                # No revelar si el email existe
                # No se envía correo, pero retornamos el mismo mensaje de éxito
                pass
            
            # Siempre retornamos el mismo mensaje de éxito
            return JsonResponse({
                'success': True,
                'message': 'Se ha enviado un correo electrónico con instrucciones para restablecer tu contraseña.'
            }, status=status.HTTP_200_OK)
            
        return JsonResponse({
            'success': False,
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@require_http_methods(["POST"])
def api_password_reset_confirm(request):
    """
    Confirmar reseteo de contraseña con token. Establece la nueva contraseña.
    """
    import json
    from rest_framework import status
    
    try:
        # Parsear JSON del body
        body = json.loads(request.body)
        serializer = PasswordResetConfirmSerializer(data=body)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            new_password = serializer.validated_data['new_password']
            
            # Establecer nueva contraseña
            user.set_password(new_password)
            user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Contraseña restablecida exitosamente. Ya puedes iniciar sesión con tu nueva contraseña.'
            }, status=status.HTTP_200_OK)
            
        return JsonResponse({
            'success': False,
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=status.HTTP_400_BAD_REQUEST)
