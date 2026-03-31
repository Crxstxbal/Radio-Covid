#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Create superuser if environment variables are set
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "from apps.users.models import User; User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists() or User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')" | python manage.py shell
fi

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
