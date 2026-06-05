"""Configuração por ambiente (dev / test / prod) via variáveis de ambiente."""
import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-troque-em-prod")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-troque-em-prod")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_EXPIRES_SECONDS", str(60 * 60 * 12)))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    # Admin inicial criado pelo seed.
    SEED_ADMIN_EMAIL = os.getenv("SEED_ADMIN_EMAIL", "admin@ragnarok.local")
    SEED_ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "admin123")
    SEED_ADMIN_NAME = os.getenv("SEED_ADMIN_NAME", "Mestre Supremo")


class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///ragnarok_dev.db"
    )


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-jwt-secret-com-32-bytes-no-minimo!!"


class ProdConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql+psycopg2://ragnarok:ragnarok@db:5432/ragnarok"
    )


_MAP = {"dev": DevConfig, "test": TestConfig, "prod": ProdConfig}


def get_config(name: str | None = None):
    name = (name or os.getenv("FLASK_CONFIG", "dev")).lower()
    return _MAP.get(name, DevConfig)
