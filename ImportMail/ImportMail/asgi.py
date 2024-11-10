"""
ASGI config for ImportMail project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from ImportMail.urls import ws_urlpatterns
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter
from channels.routing import URLRouter
from django.core.asgi import get_asgi_application
from imap_email.routing import TokenAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ImportMail.settings')

# application = get_asgi_application()
application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        TokenAuthMiddleware(  # Используем кастомный TokenAuthMiddleware
            URLRouter(ws_urlpatterns)
        ),
    ),
})
