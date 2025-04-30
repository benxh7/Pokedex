from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Cuenta, Comentario

# Formulario para registrar nuevos usuarios en la base de datos
class RegisterForm(UserCreationForm):
    class Meta:
        model = Cuenta
        # 'password1' y 'password2' vienen de UserCreationForm
        # y se usan para manejar la validación de la contraseña.
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Nombre de Usuario',
            'email': 'Correo Electrónico',
            'password1': 'Contraseña',
            'password2': 'Confirmar Contraseña'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ingresa tu nombre de usuario',
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ingresa tu contraseña',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirma tu contraseña',
        })

# Formulario para editar el perfil del usuario
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Cuenta
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})

# Formulario para editar la imagen de un perfil de usuario
class AvatarForm(forms.ModelForm):
    class Meta:
        model = Cuenta
        fields = ['imagen']
        widgets = {
            'imagen': forms.ClearableFileInput(attrs={
                'style': 'display: none;',
                'id': 'id_imagen'
            })
        }

# Formulario para crear un nuevo comentario en el foro
class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['content', 'parent']
        widgets = {
            "content": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Escribe tu comentario aquí...",
                "rows": 3,
            }),
            "parent": forms.HiddenInput(),
        }