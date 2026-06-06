"""Helpers de autenticação/autorização (JWT + RBAC)."""
from functools import wraps

from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.utils.errors import Forbidden, Unauthorized


def current_user():
    """Resolve o User autenticado a partir da identidade do JWT (ou None)."""
    from app.models.user import User

    ident = get_jwt_identity()
    if ident is None:
        return None
    return db_get_user(User, ident)


def db_get_user(User, ident):
    try:
        return User.query.get(int(ident))
    except (TypeError, ValueError):
        return None


def role_required(*roles):
    """
    Garante que há um JWT válido e que o papel do usuário está em `roles`.
    ADMIN sempre passa. Sem token -> 401; papel insuficiente -> 403.
    """
    roles = set(roles)

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user = current_user()
            if user is None:
                raise Unauthorized("Autenticação necessária.")
            if user.role != "ADMIN" and roles and user.role not in roles:
                raise Forbidden("Você não tem permissão para esta ação.")
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def auth_required(fn):
    """Apenas exige um JWT válido (qualquer papel)."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = current_user()
        if user is None:
            raise Unauthorized("Autenticação necessária.")
        return fn(*args, **kwargs)

    return wrapper
