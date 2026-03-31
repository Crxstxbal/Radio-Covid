from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer básico de usuario"""
    nombre_completo = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'nombre_completo', 'fecha_nacimiento', 'telefono',
            'es_premium', 'fecha_creacion', 'date_joined'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer para registro de usuarios"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm', 'fecha_nacimiento', 'telefono'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden")

        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError("Ya existe un usuario con este email")

        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError("Ya existe un usuario con este username")

        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer para solicitar el reseteo de contraseña"""
    email = serializers.EmailField()

    # Nota de seguridad: no validamos si el email existe en la base de datos
    # para prevenir user enumeration attacks. La vista manejará esto de forma segura


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer para confirmar el reseteo de contraseña con token"""
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)
    uid = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Las contraseñas no coinciden."})

        try:
            uid = urlsafe_base64_decode(attrs['uid']).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"uid": "Token inválido."})

        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError({"token": "Token inválido o expirado."})

        attrs['user'] = user
        return attrs
