# myapp/middleware.py

from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from imap_email.models import User


class TokenAuthMiddleware:
    """
    Аутентификация пользователя по токену из заголовков WebSocket запроса.
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Извлечение токена из заголовков WebSocket запроса
        query_params = parse_qs(scope.get("query_string", b"").decode())
        token = query_params.get("token", [None])[0]

        if token:
            user = await self.get_user_from_token(token)
            if user:
                scope['user'] = user
            else:
                scope['user'] = AnonymousUser()  # Если токен неверный
        else:
            scope['user'] = AnonymousUser()  # Если токен не передан

        # Вызов следующего middleware или consumer
        return await self.inner(scope, receive, send)

    @database_sync_to_async
    def get_user_from_token(self, token):
        """
        Метод для получения пользователя по токену.
        """
        try:
            user = User.objects.get(auth_token=token)
            return user
        except get_user_model().DoesNotExist:
            return None
