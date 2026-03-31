from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include([
        path('auth/', include('apps.users.urls')),
        path('', include('apps.radio.urls')),
    ])),
    path('dashboard/', include('dashboard.urls')),
    # URLs de usuarios para templates (con namespace diferente)
    path('users/', include('apps.users.template_urls')),
    path('', include('apps.radio.urls')),
    # Login para el dashboard
    path('dashboard/login/', auth_views.LoginView.as_view(
        template_name='dashboard/login.html',
        redirect_authenticated_user=True
    ), name='dashboard_login'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
