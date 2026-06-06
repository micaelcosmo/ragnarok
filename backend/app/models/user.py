"""Modelo de usuário e seus papéis (RBAC)."""
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models.base import TimestampMixin

PAPEIS_VALIDOS = ("ADMIN", "MESTRE", "JOGADOR")


class User(TimestampMixin, db.Model):
    """Usuário da plataforma. Papel define as permissões (ver RBAC)."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="JOGADOR")

    personagens = db.relationship(
        "Personagem", backref="dono", lazy=True, cascade="all, delete-orphan"
    )
    mesas_mestradas = db.relationship(
        "Mesa", backref="mestre", lazy=True, cascade="all, delete-orphan"
    )
    participacoes = db.relationship(
        "MembroMesa", backref="usuario", lazy=True, cascade="all, delete-orphan"
    )

    def __init__(self, email, name, password=None, role="JOGADOR"):
        self.email = (email or "").strip().lower()
        self.name = (name or "").strip()
        self.role = role if role in PAPEIS_VALIDOS else "JOGADOR"
        if password is not None:
            self.set_password(password)

    def set_password(self, password):
        """Define o hash seguro da senha."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Confere a senha contra o hash armazenado."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "ADMIN"

    def to_dict(self):
        """Serialização pública (nunca expõe o hash da senha)."""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "role": self.role,
        }
