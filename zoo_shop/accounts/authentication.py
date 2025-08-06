from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from .models import User
import jwt


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        try:
            prefix, token = auth_header.split(' ')
            if prefix.lower() != 'bearer':
                raise AuthenticationFailed('Неверный префикс токена')
        except ValueError:
            raise AuthenticationFailed('Неверный формат токена')

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Срок действия токена истёк')
        except jwt.DecodeError:
            raise AuthenticationFailed('Невалидный токен')

        try:
            user = User.objects.get(id=payload['user_id'])
        except User.DoesNotExist:
            raise AuthenticationFailed('Пользователь не найден')

        if not user.is_active:
            raise AuthenticationFailed('Аккаунт отключён')

        return (user, None)


