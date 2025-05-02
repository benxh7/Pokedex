import os
import django
from fastapi import FastAPI, HTTPException, Response
from typing import List, Union
from api.schemas import PokemonOut, PokemonStat, PokemonType
from fastapi.middleware.cors import CORSMiddleware
import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Pokedex.settings")
django.setup()

from core.models import Comentario
from django.contrib.auth import get_user_model
from api.schemas import CommentaryIn, CommentaryOut, UserOut
from api.utils import serialize_comment, serialize_user

app = FastAPI(title="Pokedex Wiki API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
    ],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Endpoint de ping
@app.get("/ping")
async def pong():
    return {"ping": "pong"}

# Endpoints de Comentarios
@app.get("/comentarios/", response_model=List[CommentaryOut])
def list_comments():
    qs = (Comentario.objects
          .filter(parent__isnull=True)
          .select_related("usuario")
          .prefetch_related("replies__usuario")
          .order_by("-created"))
    return [serialize_comment(c) for c in qs]

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