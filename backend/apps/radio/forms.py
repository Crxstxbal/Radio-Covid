from django import forms
from .models import EstacionRadio


class EstacionRadioForm(forms.ModelForm):
    class Meta:
        model = EstacionRadio
        fields = ['nombre', 'descripcion', 'stream_url', 'logo', 'activa']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la estación'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la estación'
            }),
            'stream_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://ejemplo.com/stream'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'activa': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
