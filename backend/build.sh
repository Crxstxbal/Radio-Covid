#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Create superuser if doesn't exist (non-interactive)
echo "from apps.users.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@radiocovid.com', 'admin123')" | python manage.py shell

# Create default radio station if doesn't exist
echo "
from apps.radio.models import EstacionRadio
if not EstacionRadio.objects.filter(activa=True).exists():
    EstacionRadio.objects.create(
        nombre='Radio Covid',
        descripcion='Radio online 24/7',
        stream_url='https://uk18freenew.listen2myradio.com/live.mp3?typeportmount=s1_14646_stream_416474122',
        activa=True
    )
    print('Estación creada')
else:
    print('Estación ya existe')
" | python manage.py shell
