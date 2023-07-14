import os
from contextlib import suppress

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from c3nav.urls import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "c3nav.settings")
django_asgi = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi,
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})

# optional support for static files via starlette
with suppress(ImportError):
    # settings need to be loaded after django init via get_asgi_application
    from django.conf import settings
    from starlette.applications import Starlette
    from starlette.routing import Mount
    from starlette.staticfiles import StaticFiles

    static_app = ProtocolTypeRouter({
        "http": Starlette(routes=[
            Mount(settings.STATIC_URL, app=StaticFiles(directory=settings.STATIC_ROOT), name='static'),
            Mount('/', app=django_asgi),
        ]),
        "websocket": AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        ),
    })
