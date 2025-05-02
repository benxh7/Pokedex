from django.urls import path, include
from .views import home, error_404, login_view, register_view, logout_view, mi_cuenta_view, mi_cuenta_editar_view, \
    cambiar_contraseña_view, pokedex, pokemons, pokemons_detalles, post_view, \
    comment_edit, comment_delete, external_posts, ver_cuentas_api, user_delete

# Aqui debemos añadir las urls de la app core
urlpatterns = [
    path('register/', register_view, name='registrarse'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('micuenta/', mi_cuenta_view, name='micuenta'),
    path('micuenta_editar/', mi_cuenta_editar_view, name='micuenta_editar'),
    path('cambiar_contraseña/', cambiar_contraseña_view, name='cambiar_contraseña'),
    path('', home, name='home'),
    path('pokedex', pokedex, name='pokedex'),
    path('pokemons', pokemons, name='pokemons'),
    path('pokemon/<int:id>/', pokemons_detalles, name='pokemon'),
    path('error_404', error_404, name='error_404'),
    path('post_comunidad', post_view, name='post'),
    path('comentario/<int:pk>/editar/', comment_edit, name="comment_edit"),
    path('comentario/<int:pk>/borrar/', comment_delete, name="comment_delete"),
    path('external_posts/', external_posts, name='external_posts'),
    path('ver_cuentas_api', ver_cuentas_api, name='ver_cuentas_api'),
    path('usuario/<int:pk>/borrar/', user_delete, name='user_delete'),
    path('accounts/', include('django.contrib.auth.urls')),
]
