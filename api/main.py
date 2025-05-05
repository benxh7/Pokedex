import os
import django
from fastapi import FastAPI, HTTPException, Depends, Response
from typing import List, Union
from datetime import timedelta

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from api.schemas import PokemonOut, PokemonStat, PokemonType
from fastapi.middleware.cors import CORSMiddleware
import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Pokedex.settings")
django.setup()

from core.models import Comentario, Usuario, AuthToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from api.schemas import CommentaryIn, CommentaryOut, UserOut
from api.utils import serialize_comment, serialize_user

# CONFIGURACIÓN

# Tiempo de expiracion del token 1 hora
# despues de pasado 1 hora este se borra automaticamente
TOKEN_TTL_MINUTES = 60

# Configuración de la autenticacion esto lee token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Verificamos credenciales enviadas al endpoint /token
# Esta definicion devuelve una instancia de Usuario, solamente si
# el nombre existe en la DB y si la contraseña coincide.
# si no existe el usuario o la contraseña no coincide devuelve None
def authenticate_user(username: str, password: str):
    try:
        user = Usuario.objects.get(username=username)
    except Usuario.DoesNotExist:
        return None
    return user if user.check_password(password) else None


# Creamos y almacenamos un token para el usuario
def issue_token(user: Usuario) -> AuthToken:
    return AuthToken.objects.create(
        user=user,
        expires_at=timezone.now() + timedelta(minutes=TOKEN_TTL_MINUTES)
    )


# Dependencia para los endpoints protegidos, esto
# extrae la clave token enviada por FastAPI, tambien
# busca la key en la tabla de AuthToken, verifica la expiracion
# y si todó esta bien devuelve el usuario asociado a ese token
def get_current_user(token: str = Depends(oauth2_scheme)) -> Usuario:
    try:
        t = AuthToken.objects.select_related('user').get(pk=token)
    except AuthToken.DoesNotExist:
        raise HTTPException(401, "Token inválido")

    if t.is_expired():
        t.delete()
        raise HTTPException(401, "Token caducado")

    return t.user


# FASTAPI
app = FastAPI(title="Pokédex Wiki API")

# Configuracion del metodo CORS
# Permitir el acceso a la API desde el frontend
# es un mecanismo de seguridad que permite o restringe el acceso a recursos
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
    ],
    allow_methods=["GET"],
    allow_headers=["*"],
)


# AUTENTICACIÓN LOGIN Y LOGOUT
@app.post("/token")
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form.username, form.password)
    if not user:
        raise HTTPException(401, "Credenciales incorrectas")

    token = issue_token(user)
    return {"access_token": token.key, "token_type": "bearer",
            "expires_in": TOKEN_TTL_MINUTES * 60}


@app.delete("/token", status_code=204)
def logout(token: str = Depends(oauth2_scheme),
           current: Usuario = Depends(get_current_user)):
    AuthToken.objects.filter(pk=token, user=current).delete()
    return Response(status_code=204)


# ENDPOINTS PUBLICOS
@app.get("/ping")
async def pong():
    return {"ping": "pong"}


@app.get("/comentarios/", response_model=List[CommentaryOut])
def list_comments():
    qs = (Comentario.objects
          .filter(parent__isnull=True)
          .select_related("usuario")
          .prefetch_related("replies__usuario")
          .order_by("-created"))
    return [serialize_comment(c) for c in qs]


# Endpoints de Usuarios
User = get_user_model()


@app.get("/usuarios/", response_model=List[UserOut])
def list_users():
    qs = User.objects.order_by("date_joined")
    return [serialize_user(u) for u in qs]


@app.get("/usuarios/{pk}/", response_model=UserOut)
def get_user(pk: int):
    try:
        u = User.objects.get(pk=pk)
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return serialize_user(u)


# Endpoints para traer datos de un Pokemon
@app.get("/pokemon/{identifier}", response_model=PokemonOut)
def get_pokemon(identifier: Union[int, str]):
    url = f"https://pokeapi.co/api/v2/pokemon/{str(identifier).lower()}"
    resp = requests.get(url, timeout=5)
    if resp.status_code == 404:
        raise HTTPException(404, "Pokémon no encontrado")
    data = resp.json()

    stats = [PokemonStat(name=s["stat"]["name"], base_stat=s["base_stat"])
             for s in data["stats"]]
    types = [PokemonType(name=t["type"]["name"]) for t in data["types"]]

    return PokemonOut(
        id=data["id"],
        name=data["name"],
        stats=stats,
        types=types,
        sprite=data["sprites"]["front_default"] or ""
    )


# ENDPOINTS PRIVADOS
@app.post("/comentarios/", response_model=CommentaryOut)
def create_comment(payload: CommentaryIn,current: Usuario = Depends(get_current_user)):
    c = Comentario.objects.create(
        content=payload.content,
        parent_id=payload.parent,
        usuario=current
    )
    return serialize_comment(c)


@app.put("/comentarios/{pk}/", response_model=CommentaryOut)
def update_comment(pk: int,payload: CommentaryIn,current: Usuario = Depends(get_current_user)):
    try:
        c = Comentario.objects.get(pk=pk)
    except Comentario.DoesNotExist:
        raise HTTPException(404, "Comentario no encontrado")

    # Solo permite que el autor o el superuser editen el comentario
    if c.usuario != current and not current.is_superuser:
        raise HTTPException(403, "No tienes permiso para editar este comentario")

    c.content = payload.content
    c.parent_id = payload.parent
    c.save()
    return serialize_comment(c)


@app.delete("/comentarios/{pk}/", status_code=204)
def delete_comment(pk: int, current: Usuario = Depends(get_current_user)):
    try:
        c = Comentario.objects.get(pk=pk)
    except Comentario.DoesNotExist:
        raise HTTPException(404, "Comentario no encontrado")

    # Solo permite que el autor o el superuser borren el comentario
    if c.usuario != current and not current.is_superuser:
        raise HTTPException(403, "No tienes permiso para borrar este comentario")

    c.delete()
    return Response(status_code=204)
