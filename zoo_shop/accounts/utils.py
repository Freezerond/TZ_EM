import jwt
from django.conf import settings
from datetime import datetime, timedelta


def jwt_pair_for_user(user):
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(minutes=60),
        'iat': datetime.utcnow()
    }

    access = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    refresh_payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow()
    }
    refresh = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')

    return {
        "access": access,
        "refresh": refresh
    }



