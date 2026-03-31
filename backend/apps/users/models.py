from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Modelo de usuario personalizado"""
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    es_premium = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.email

    @property
    def nombre_completo(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
