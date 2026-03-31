# Radio Web - Página de Radio Simplificada

Una aplicación web moderna para radio streaming con contador de usuarios conectados en tiempo real.

## Características Principales

- 🎵 **Reproductor de Radio en Vivo**: Streaming de audio con controles intuitivos
- 👥 **Contador de Oyentes**: Muestra cuántas personas están escuchando en tiempo real
- 🎶 **Información de Canciones**: Muestra la canción actual que está sonando
- 📱 **Diseño Responsivo**: Funciona perfectamente en desktop y móviles
- ⚡ **Tiempo Real**: Actualizaciones instantáneas usando WebSockets
- 🎨 **Interfaz Moderna**: Diseño atractivo con Tailwind CSS y Framer Motion

## Arquitectura

### Backend (Django)
- **Framework**: Django 5.2 con Django REST Framework
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **WebSockets**: Django Channels para comunicación en tiempo real
- **Apps**:
  - `radio`: Gestión de estación, oyentes y canciones
  - `users`: Sistema de autenticación personalizado

### Frontend (React)
- **Framework**: React 18 con Vite
- **Estilos**: Tailwind CSS
- **Animaciones**: Framer Motion
- **HTTP Client**: Axios
- **WebSockets**: Cliente WebSocket nativo

## Instalación

### Backend

1. Crear entorno virtual:
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:
```bash
copy .env.example .env
# Editar .env con tus configuraciones
```

4. Aplicar migraciones:
```bash
python manage.py migrate
```

5. Crear superusuario:
```bash
python manage.py createsuperuser
```

6. Iniciar servidor:
```bash
# Con WebSockets
python -m daphne -b 0.0.0.0 -p 8000 radio_web.asgi:application

# Sin WebSockets
python manage.py runserver
```

### Frontend

1. Instalar dependencias:
```bash
cd frontend
npm install
```

2. Iniciar servidor de desarrollo:
```bash
npm run dev
```

3. Para producción:
```bash
npm run build
```

## Configuración

### Variables de Entorno (Backend)

```env
SECRET_KEY=tu-clave-secreta
DEBUG=True
USE_SQLITE=True
FRONTEND_URL=http://localhost:3000
RADIO_STREAM_URL=https://tu-streaming-url.com/stream
RADIO_NAME=Tu Radio
RADIO_DESCRIPTION=Descripción de tu radio
```

### Variables de Entorno (Frontend)

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## API Endpoints

### Radio
- `GET /api/estacion/activa/` - Obtener estación activa
- `GET /api/estacion/info_streaming/` - Información del streaming
- `GET /api/oyentes/conteo_actual/` - Conteo de oyentes actuales
- `POST /api/oyentes/registrar_conexion/` - Registrar nueva conexión
- `POST /api/oyentes/desconexion/` - Registrar desconexión

### Canciones
- `GET /api/canciones/actual/` - Obtener canción actual
- `POST /api/canciones/actualizar/` - Actualizar canción actual

### WebSocket
- `ws://localhost:8000/ws/radio/` - Conexión WebSocket para actualizaciones en tiempo real

## Estructura del Proyecto

```
pagina-web-radio/
├── backend/
│   ├── apps/
│   │   ├── radio/          # Gestión de radio y oyentes
│   │   └── users/          # Sistema de usuarios
│   ├── radio_web/          # Configuración Django
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # Componentes React
│   │   ├── pages/          # Páginas
│   │   ├── services/        # Servicios API
│   │   └── hooks/          # Hooks personalizados
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Uso

1. Inicia el backend de Django
2. Inicia el frontend de React
3. Abre http://localhost:3000 en tu navegador
4. Presiona play en el reproductor para comenzar a escuchar
5. El contador de oyentes se actualizará automáticamente

## Características Técnicas

### Conteo de Oyentes
- Usa WebSockets para actualizaciones en tiempo real
- Limpia automáticamente oyentes inactivos (5 minutos)
- Registra estadísticas diarias

### Reproductor de Audio
- Soporte para streaming HTTP/HTTPS
- Controles de volumen
- Indicadores visuales de reproducción
- Manejo automático de reconexión

### Diseño Responsivo
- Mobile-first approach
- Componentes adaptables
- Optimizado para diferentes tamaños de pantalla

## Despliegue

### Backend (Render)
```bash
# Build Command
pip install -r requirements.txt

# Start Command
daphne -b 0.0.0.0 -p $PORT radio_web.asgi:application
```

### Frontend (Vercel/Netlify)
```bash
# Build Command
npm run build

# Output Directory
dist
```

## Contribuir

1. Fork el proyecto
2. Crear una rama (`git checkout -b feature/nueva-caracteristica`)
3. Commit cambios (`git commit -am 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear Pull Request

## Licencia

Este proyecto es de uso privado y está desarrollado para fines educativos.
