from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.conf import settings
import uuid

def generate_username():
    return f"user_{uuid.uuid4().hex[:8]}"

class Cuenta(AbstractUser):
    # Hacemos que el email sea unico para cada cuenta de usuario.
    email = models.EmailField(unique=True)
    imagen = models.ImageField(upload_to='fotos_perfil', null=True, default='default/user.png')

    def save(self, *args, **kwargs):
        # Si no tiene username manualmente ingresado, generarlo
        if not self.username:
            self.username = generate_username()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

# Borramos la imagen de perfil anterior al guardar una nueva
@receiver(pre_save, sender=Cuenta)
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
@receiver(post_delete, sender=Cuenta)
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
