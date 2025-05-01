from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Usuario, Comentario

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        label="Contraseña"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirmar Contraseña"
    )

    class Meta:
        model  = Usuario
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplica form-control y placeholder automáticamente
        for field_name in ['username', 'email', 'password1', 'password2']:
            field = self.fields[field_name]
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
            })

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    username = forms.CharField(label="Nombre de Usuario")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")

    def clean(self):
        cleaned = super().clean()
        uname = cleaned.get('username')
        pwd   = cleaned.get('password')
        try:
            user = Usuario.objects.get(username=uname)
        except Usuario.DoesNotExist:
            raise forms.ValidationError("Usuario o contraseña inválidos.")
        if not user.check_password(pwd):
            raise forms.ValidationError("Usuario o contraseña inválidos.")
        cleaned['user'] = user
        return cleaned

# Formulario para editar el perfil del usuario
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})

# Formulario para editar la imagen de un perfil de usuario
class AvatarForm(forms.ModelForm):
    class Meta:
        model = Usuario
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