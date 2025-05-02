from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout, login, update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from .forms import RegisterForm, LoginForm, EditProfileForm, AvatarForm, ComentarioForm
from .models import Comentario
from datetime import datetime
import requests


def ver_cuentas_api(request):
    try:
        # IMPORTANTE LA OBTENCION DEL PUERTO AQUI PARA ACCEDER A LA API
        response = requests.get("http://127.0.0.1:8001/usuarios/", timeout=5)
        response.raise_for_status()
        cuentas = response.json()
        for c in cuentas:
            ts = c.get("date_joined_ts")  # p.ej. 1713656700
            if ts is not None:
                c["date_joined"] = datetime.utcfromtimestamp(ts)
    except requests.RequestException as e:  # usa el módulo 'requests'
        cuentas = []
        print(f'Error al obtener las cuentas: {e}')
    return render(request, 'core/ver_cuentas_api.html', {'cuentas': cuentas})


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save() # Se guarda el usuario en la DB con contraseña hasheada
            login(request, user)
            messages.success(request, f'Bienvenido, {user.username}!')
            return redirect('home') # Redirige a la url que desees
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            request.session['user_id'] = user.id
            messages.success(request, f'¡Hola de nuevo, {user.username}!')
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


@login_required
def mi_cuenta_view(request):
    # Formulario para cambiar imagen de perfil
    form = AvatarForm(request.POST or None, request.FILES or None, instance=request.user)

    if request.method == 'POST' and form.is_valid():
        form.save()  # Guarda la nueva imagen en el campo 'imagen'
        messages.success(request, "Avatar actualizado correctamente.")
        return redirect('micuenta')  # Refresca la misma página

    return render(request, 'registration/micuenta.html', {'form': form, })


@login_required
def mi_cuenta_editar_view(request):
    user = request.user  # El usuario logueado actual
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Tu perfil se ha actualizado correctamente!')
            return redirect('micuenta')  # O la ruta que definas
        else:
            messages.error(request, 'Por favor corrige los errores señalados.')
    else:
        form = EditProfileForm(instance=user)

    return render(request, 'registration/micuenta_editar.html', {'form': form})


@login_required
def cambiar_contraseña_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, '¡Tu contraseña se ha cambiado exitosamente!')
            return redirect('micuenta')
        else:
            if 'old_password' in form.errors:
                messages.error(request, 'Contraseña antigua incorrecta.')
            else:
                messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'registration/cambiar_contraseña.html', {'form': form})


def logout_view(request):
    logout(request)  # Cierra la sesión
    return redirect('core/home')


def home(request):
    return render(request, 'core/home.html')

def error_404(request):
    return render(request, 'core/error_404.html')

def pokedex(request):
    return render(request, 'core/pokedex.html')

def pokemons(request):
    return render(request, 'core/pokemons.html')

def pokemons_detalles(request, id):
    url = f"http://127.0.0.1:8001/pokemon/{id}"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
    except requests.RequestException:
        # tanto tiempo de espera como 4xx/5xx
        raise Http404("Pokémon no encontrado")

    pokemon = resp.json()
    return render(request, 'core/pokemon_detalles.html', {
        'pokemon': pokemon
    })

@login_required
def foro_view(request):
    comentarios = Comentario.objects.filter(parent__isnull=True).select_related('usuario').prefetch_related(
        'replies__usuario')

    form = ComentarioForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        nuevo = form.save(commit=False)
        nuevo.usuario = request.user
        nuevo.save()
        return redirect('foro')

    return render(request, 'core/foro.html', {
        'comentarios': comentarios,
        'form': form,
    })


@login_required
def comment_edit(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)
    # Permiso para editar
    if comentario.usuario != request.user and not request.user.is_superuser:
        messages.error(request, "No tienes permiso para editar este comentario.")
    else:
        if request.method == 'POST':
            form = ComentarioForm(request.POST, instance=comentario)
            if form.is_valid():
                form.save()
                messages.success(request, "Comentario editado correctamente.")
            else:
                messages.error(request, "Hubo un error al editar el comentario.")
    return redirect('foro')


@login_required
def comment_delete(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)
    if comentario.usuario != request.user and not request.user.is_superuser:
        messages.error(request, "No tienes permiso para borrar este comentario.")
    else:
        comentario.delete()
        messages.success(request, "Comentario borrado.")
    return redirect('foro')


# Vista para obtener publicaciones externas sobre el juego mediante una API
# de esta forma el usuario puede tener datos o informacion de otras fuentes
def external_posts(request):
    url = "https://www.reddit.com/r/PokemonES/new.json?limit=12"
    headers = {"User-Agent": "TheForestWikiApp/0.1"}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        posts = []
        for child in data.get("data", {}).get("children", []):
            d = child["data"]
            posts.append({
                "title": d["title"],
                "author": d["author"],
                "created": datetime.utcfromtimestamp(d["created_utc"]),
                "permalink": "https://reddit.com" + d["permalink"],
                "url": d.get("url")
            })
    except requests.RequestException:
        posts = []
    return render(request, "core/posts_externos.html", {"posts": posts})

# El superuser va a poder eliminar cuentas desde su panel de ver_cuentas_api con ayuda de FastAPI
User = get_user_model()

@login_required
@user_passes_test(lambda u: u.is_superuser)
def user_delete(request, pk):
    if request.method == 'POST':
        try:
            target = User.objects.get(pk=pk)
            if target == request.user:
                messages.error(request, "No puedes eliminar tu propia cuenta aquí.")
            else:
                target.delete()
                messages.success(request, f"Cuenta de {target.username} eliminada.")
        except User.DoesNotExist:
            messages.error(request, "Usuario no encontrado.")
    return redirect('ver_cuentas_api')
