import os

from channels.auth import AuthMiddlewareStack, get_user
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chat_application.settings")
django_asgi_app = get_asgi_application()  # Initialize ASGI app

from chat import routing  # Import your routing


class JWTAuthMiddleware:
    """
    Custom middleware to authenticate users using JWT tokens.
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        user = await get_user(scope)
        scope['user'] = user
        return await self.inner(scope, receive, send)


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(  # Use AuthMiddlewareStack to include Django's authentication
            URLRouter(
                routing.websocket_urlpatterns
            )
        )
    ),
})
