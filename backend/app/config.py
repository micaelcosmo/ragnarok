"""
Configuração por ambiente (dev / test / prod) via variáveis de ambiente.

Segurança:
- NENHUM segredo hardcoded. Em dev/test, se a variável não vier do ambiente, geramos um
  valor EFÊMERO aleatório por execução (não persiste, não vaza).
- Em produção, segredos são OBRIGATÓRIOS: `ProdConfig.validate()` aborta o boot (fail-fast)
  se faltarem `SECRET_KEY`, `JWT_SECRET_KEY` ou `DATABASE_URL`.
"""
import os
import secrets

# Variáveis obrigatórias em produção (sem default).
OBRIGATORIAS_PROD = ("SECRET_KEY", "JWT_SECRET_KEY", "DATABASE_URL")


def _segredo_dev(nome: str) -> str:
    """Valor do ambiente, ou um efêmero aleatório (apenas dev/test) — nunca hardcoded."""
    return os.getenv(nome) or secrets.token_hex(32)


class Config:
    SECRET_KEY = _segredo_dev("SECRET_KEY")
    JWT_SECRET_KEY = _segredo_dev("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_EXPIRES_SECONDS", str(60 * 60 * 12)))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    # Uploads de imagem (retrato/símbolo). Pasta servida por nginx (volume) em runtime.
    UPLOAD_DIR = os.getenv(
        "UPLOAD_DIR",
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads"),
    )
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_UPLOAD_BYTES", str(2 * 1024 * 1024 + 8192)))  # ~2MB + overhead
    # Admin inicial criado pelo seed (sem senha default — o seed gera uma se faltar).
    SEED_ADMIN_EMAIL = os.getenv("SEED_ADMIN_EMAIL", "admin@ragnarok.local")
    SEED_ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD")  # sem default
    SEED_ADMIN_NAME = os.getenv("SEED_ADMIN_NAME", "Administrador")

    @staticmethod
    def validate():
        """Validação de boot (no-op em dev/test)."""


class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///ragnarok_dev.db")


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # JWT herda o segredo EFÊMERO do base Config (token_hex aleatório por processo) —
    # estável durante a sessão de testes e sem nenhum literal de segredo no código.


class ProdConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "")

    @staticmethod
    def validate():
        """Aborta o boot se algum segredo obrigatório estiver ausente."""
        faltando = [nome for nome in OBRIGATORIAS_PROD if not os.getenv(nome)]
        if faltando:
            raise RuntimeError(
                "Configuração de produção inválida — variáveis obrigatórias ausentes: "
                + ", ".join(faltando)
                + ". Defina-as no .env (nunca hardcode segredos)."
            )


_MAP = {"dev": DevConfig, "test": TestConfig, "prod": ProdConfig}


def get_config(name: str | None = None):
    name = (name or os.getenv("FLASK_CONFIG", "dev")).lower()
    return _MAP.get(name, DevConfig)
