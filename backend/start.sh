#!/bin/bash
# Script de inicio para Render - ejecuta migraciones y luego inicia el servidor

echo "[START] Ejecutando migraciones..."
python manage.py migrate --noinput

echo "[START] Verificando superusuario..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    print('[START] Creando superusuario admin...')
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('[START] Superusuario creado: admin / admin123')
else:
    print('[START] Superusuario admin ya existe')
EOF

echo "[START] Iniciando servidor..."
gunicorn radio_web.wsgi:application
