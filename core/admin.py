from django.contrib import admin
from .models import Usuario

class RegistroAdmin(admin.ModelAdmin):
    list_display = ('username', 'email',)
    search_fields = ('username', 'email',)

admin.site.register(Usuario, RegistroAdmin)