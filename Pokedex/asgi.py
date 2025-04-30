"""
ASGI config for Pokedex project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from starlette.applications import Starlette
from starlette.routing import Mount

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Pokedex.settings")
django_asgi_app = get_asgi_application()

from api.main import app as fastapi_app

application = Starlette(
    debug=True,
    routes=[
        Mount("/api", fastapi_app),
        Mount("/",    django_asgi_app),
    ],
)
