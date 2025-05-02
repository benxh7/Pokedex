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

# Tiempo de expiración del token 1 hora
TOKEN_TTL_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def authenticate_user(username: str, password: str):
    try:
        user = Usuario.objects.get(username=username)
    except Usuario.DoesNotExist:
        return None
    return user if user.check_password(password) else None


def issue_token(user: Usuario) -> AuthToken:
    return AuthToken.objects.create(
        user=user,
        expires_at=timezone.now() + timedelta(minutes=TOKEN_TTL_MINUTES)
    )


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
app = FastAPI(title="Pokedex Wiki API")

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
def create_comment(payload: CommentaryIn):
    User = get_user_model()
    usuario = User.objects.first()
    c = Comentario.objects.create(
        content=payload.content,
        parent_id=payload.parent,
        usuario=usuario
    )
    return serialize_comment(c)


@app.put("/comentarios/{pk}/", response_model=CommentaryOut)
def update_comment(pk: int, payload: CommentaryIn):
    try:
        c = Comentario.objects.get(pk=pk)
    except Comentario.DoesNotExist:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")
    c.content = payload.content
    c.parent_id = payload.parent
    c.save()
    return serialize_comment(c)


@app.delete("/comentarios/{pk}/", status_code=204)
def delete_comment(pk: int):
    try:
        Comentario.objects.get(pk=pk).delete()
    except Comentario.DoesNotExist:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")
    return Response(status_code=204)
