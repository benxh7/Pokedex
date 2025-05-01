from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import UserManager
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.conf import settings
import uuid


def generate_username():
    return f"user_{uuid.uuid4().hex[:8]}"


class Usuario(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    imagen = models.ImageField(
        upload_to='fotos_perfil', null=True, blank=True,
        default='default/user.png'
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    @classmethod
    def normalize_username(cls, username):
        """
        Devuelve la versión “limpia” del username.
        Django la usa internamente en createsuperuser.
        """
        return username.strip() if isinstance(username, str) else username

    is_anonymous = False
    is_authenticated = True

    objects = UserManager()

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def natural_key(self):
        return (self.username,)

    def has_perm(self, perm, obj=None):
        """
        ¿Este usuario tiene el permiso `perm`?
        Para simplificar, devolvemos True solo si es superuser.
        """
        return bool(self.is_superuser)

    def has_module_perms(self, app_label):
        """
        ¿Este usuario puede ver el módulo (app) `app_label`?
        Aquí devolvemos True solo a superusuarios o staff.
        """
        return bool(self.is_staff)

    def __str__(self):
        return self.username


# Borramos la imagen de perfil anterior al guardar una nueva
@receiver(pre_save, sender=Usuario)
def borrar_imagen_antigua(sender, instance, **kwargs):
    if not instance.pk:
        return  # No hay imagen anterior
    try:
        viejo = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    # Si la imagen ha cambiado, borramos la anterior
    if viejo.imagen and viejo.imagen.name != instance.imagen.name:
        viejo.imagen.delete(save=False)


# Borramos la imagen al eliminar la cuenta
@receiver(post_delete, sender=Usuario)
def borrar_imagen_al_eliminar(sender, instance, **kwargs):
    if instance.imagen:
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
