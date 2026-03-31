from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .forms import CustomUserCreationForm, UserLoginForm, UserProfileForm


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
            return Response({'success': False, 'error': 'Todos los campos son requeridos'}, status=status.HTTP_400_BAD_REQUEST)
        
        if password1 != password2:
            return Response({'success': False, 'error': 'Las contraseñas no coinciden'}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(password1) < 6:
            return Response({'success': False, 'error': 'La contraseña debe tener al menos 6 caracteres'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            return Response({'success': False, 'error': 'El nombre de usuario ya existe'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({'success': False, 'error': 'El email ya está registrado'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        
        return Response({'success': True, 'message': 'Usuario creado exitosamente'}, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    """API de login para el frontend"""
    try:
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            return Response({'success': False, 'error': 'Usuario y contraseña son requeridos'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        
        if user:
            login(request, user)
            return Response({
                'success': True, 
                'message': 'Login exitoso',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'error': 'Usuario o contraseña incorrectos'}, status=status.HTTP_401_UNAUTHORIZED)
            
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Vistas de templates (para uso directo en Django)
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from .models import User
from .serializers import UserSerializer, UserRegistrationSerializer
from .forms import CustomUserCreationForm, UserLoginForm, UserProfileForm


# Vistas API separadas para registro y login (sin autenticación requerida)
@csrf_exempt
@require_http_methods(["POST"])
def api_register(request):
    """API endpoint para registro de usuarios"""
    try:
        data = json.loads(request.body)
        
        # Validar que los campos requeridos estén presentes
        if not all(key in data for key in ['username', 'email', 'password1', 'password2']):
            return Response({
                'success': False,
                'message': 'Faltan campos requeridos'
            }, status=400)
        
        # Validar que las contraseñas coincidan
        if data['password1'] != data['password2']:
            return Response({
                'success': False,
                'message': 'Las contraseñas no coinciden'
            }, status=400)
        
        # Crear formulario con los datos
        form_data = {
            'username': data['username'],
            'email': data['email'],
            'password1': data['password1'],
            'password2': data['password2']
        }
        
        form = CustomUserCreationForm(form_data)
        if form.is_valid():
            user = form.save()
            return Response({
                'success': True, 
                'message': 'Usuario registrado correctamente'
            })
        else:
            return Response({
                'success': False, 
                'errors': form.errors
            }, status=400)
            
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'message': 'Error en el formato de los datos'
        }, status=400)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error del servidor: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    """API endpoint para login de usuarios"""
    try:
        data = json.loads(request.body)
        
        # Validar campos requeridos
        if not all(key in data for key in ['username', 'password']):
            return Response({
                'success': False,
                'message': 'Faltan campos requeridos'
            }, status=400)
        
        # Crear formulario con los datos
        form_data = {
            'username': data['username'],
            'password': data['password']
        }
        
        form = UserLoginForm(form_data)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                return Response({
                    'success': True, 
                    'message': 'Sesión iniciada correctamente',
                    'user': {
                        'username': user.username,
                        'email': user.email
                    }
                })
            else:
                return Response({
                    'success': False,
                    'message': 'Usuario o contraseña incorrectos'
                }, status=400)
        else:
            return Response({
                'success': False,
                'errors': form.errors
            }, status=400)
            
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'message': 'Error en el formato de los datos'
        }, status=400)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error del servidor: {str(e)}'
        }, status=500)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de usuarios (requiere autenticación)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], permission_classes=[])
    def register(self, request):
        """Registrar nuevo usuario"""
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, '¡Cuenta creada exitosamente! Ahora puedes iniciar sesión.')
            return Response({'success': True, 'message': 'Usuario registrado correctamente'})
        else:
            return Response({
                'success': False, 
                'errors': form.errors
            }, status=400)

    @action(detail=False, methods=['post'], permission_classes=[])
    def user_login(self, request):
        """Iniciar sesión de usuario"""
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                return Response({'success': True, 'message': 'Sesión iniciada correctamente'})
            else:
                return Response({
                    'success': False,
                    'message': 'Usuario o contraseña incorrectos'
                }, status=400)
        else:
            return Response({
                'success': False,
                'errors': form.errors
            }, status=400)

    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Obtener perfil del usuario actual"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def update_profile(self, request):
        """Actualizar perfil del usuario"""
        user = request.user
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        
        if form.is_valid():
            form.save()
            return Response({'success': True, 'message': 'Perfil actualizado correctamente'})
        else:
            return Response({
                'success': False,
                'errors': form.errors
            }, status=400)

    @action(detail=False, methods=['get'])
    def list_users(self, request):
        """Listar todos los usuarios (solo para admin)"""
        if not request.user.is_staff:
            return Response({'error': 'No autorizado'}, status=403)
        
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
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=user)
    
    return render(request, 'users/profile.html', {'form': form, 'user': user})


def logout_view(request):
    """Vista de logout"""
    logout(request)
    messages.success(request, '¡Sesión cerrada correctamente!')
    return redirect('/')

