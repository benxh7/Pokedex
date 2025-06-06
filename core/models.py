from django.core.mail import send_mail
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import UserManager
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone
import secrets

DEFAULT_USER_IMAGE = 'default/user.png'

class Usuario(models.Model):
    # Definimos el modelo de usuario con sus datos
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    imagen = models.ImageField(
        upload_to='fotos_perfil', null=True, blank=True,
        default=DEFAULT_USER_IMAGE
    )

    # Definimos el modelo de usuario como el modelo por defecto
    # como email y username
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    # Definimos el manager para el modelo de usuario
    objects = UserManager()

    # Eliminamos espacios al inicio o al final de los nombres
    @classmethod
    def normalize_username(cls, username):
        return username.strip() if isinstance(username, str) else username

    # Agregamos unos atributos fijos para tener compatibilidad con el sistema de autenticacion
    is_anonymous = False
    is_authenticated = True

    # Generamos y guardamos el hash de la contraseña
    # esto para evitar guardar la contraseña sin encriptar
    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def set_unusable_password(self):
        self.password = make_password(None)

    def has_usable_password(self):
        return self.password is not None and not self.password.startswith('!')

    # Verificamos si el raw_password coincide con el primer hash
    # que ya almacenamos en la base de datos arriba
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    @classmethod
    def get_email_field_name(cls):
        return cls.EMAIL_FIELD

    # Simula el envio de un correo electronico al usuario
    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    # Ahora definimos la presentacion unica neutral por nombre de usuario
    def natural_key(self):
        return (self.username,)

    # Permisos individuales solo para el superusuario
    def has_perm(self, perm, obj=None):
        return bool(self.is_superuser)

    # Permiso para ver apps en admin si es un administrador/superusuario
    def has_module_perms(self, app_label):
        return bool(self.is_staff)

    # El nombre de usuario
    def __str__(self):
        return self.username


class AuthToken(models.Model):
    key = models.CharField(max_length=40, primary_key=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='auth_tokens', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    @staticmethod
    def generate_key():
        return secrets.token_urlsafe(20)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        super().save(*args, **kwargs)

    def is_expired(self):
        return self.expires_at and timezone.now() >= self.expires_at


# Si el usuario cambia su foto, eliminamos la anterior
# solo si no es la imagen generada automaticamente
@receiver(pre_save, sender=Usuario)
def borrar_imagen_antigua(sender, instance, **kwargs):
    if not instance.pk:
        return  # No hay imagen anterior
    try:
        viejo = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    # Si la imagen ha cambiado, borramos la anterior
    if (
            viejo.imagen
            and viejo.imagen.name != DEFAULT_USER_IMAGE
            and viejo.imagen.name != instance.imagen.name
    ):
        viejo.imagen.delete(save=False)


# Cuando eliminemos la cuenta, quitamos la foto de perfil tambien
# excepto si es la imagen generada automaticamente
@receiver(post_delete, sender=Usuario)
def borrar_imagen_al_eliminar(sender, instance, **kwargs):
    if instance.imagen and instance.imagen.name != DEFAULT_USER_IMAGE:
        instance.imagen.delete(save=False)


class Comentario(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    content = models.TextField('Contenido')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey(
        'self',
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='replies',
        help_text='Comentario al que responde',
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'

    def __str__(self):
        return f"{self.user.username}: {self.contenido[:20]}"
