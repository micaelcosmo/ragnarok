"""Mixins reutilizáveis para os modelos."""
from datetime import datetime, timezone

from app.extensions import db


def agora_utc() -> datetime:
    """Instante atual em UTC (timezone-aware)."""
    return datetime.now(timezone.utc)


class TimestampMixin:
    """Adiciona created_at automático aos modelos que herdarem."""

    created_at = db.Column(db.DateTime, default=agora_utc, nullable=False)
