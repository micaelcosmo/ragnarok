"""Endpoint de healthcheck (público)."""
from flask import Blueprint

from app.utils.responses import ok

bp = Blueprint("health", __name__)


@bp.get("/health")
def health():
    """Verificação de saúde da API."""
    return ok({"status": "ok", "service": "ragnarok-api", "version": "v1"})
