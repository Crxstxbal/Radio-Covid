from django.shortcuts import render, redirect
from django.contrib import messages
from apps.users.models import User

def first_time_setup(request):
    """
    Vista para crear el primer superusuario.
    Solo funciona si no hay superusuarios en la base de datos.
    """
    # Si ya existe un superuser, redirigir al admin
    if User.objects.filter(is_superuser=True).exists():
        return redirect('/admin/')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        password2 = request.POST.get('password2', '').strip()
        
        errors = []
        
        if not username:
            errors.append('El nombre de usuario es requerido')
        if not email:
            errors.append('El email es requerido')
        if not password:
            errors.append('La contraseña es requerida')
        if password != password2:
            errors.append('Las contraseñas no coinciden')
        if len(password) < 6:
            errors.append('La contraseña debe tener al menos 6 caracteres')
        
        if errors:
            return render(request, 'setup/first_time.html', {
                'errors': errors,
                'username': username,
                'email': email
            })
        
        # Crear superuser
        try:
            User.objects.create_superuser(username, email, password)
            messages.success(request, f'Superusuario "{username}" creado exitosamente. Ya puedes iniciar sesión.')
            return redirect('/admin/')
        except Exception as e:
            return render(request, 'setup/first_time.html', {
                'errors': [str(e)],
                'username': username,
                'email': email
            })
    
    return render(request, 'setup/first_time.html')
