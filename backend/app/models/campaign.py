"""Modelos de Mesa (campanha) e seus membros."""
import secrets
import string

from app.extensions import db
from app.models.base import TimestampMixin

_ALFABETO_CODIGO = string.ascii_uppercase + string.digits


class Mesa(TimestampMixin, db.Model):
    """Mesa (campanha) gerenciada por um mestre, com jogadores convidados."""

    __tablename__ = "mesas"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    sistema = db.Column(db.String(60), default="D&D 5E", nullable=False)
    codigo_convite = db.Column(db.String(8), unique=True, nullable=False, index=True)
    mestre_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    membros = db.relationship(
        "MembroMesa", backref="mesa", lazy=True, cascade="all, delete-orphan"
    )
    personagens = db.relationship("Personagem", backref="mesa", lazy=True)
    monstros = db.relationship(
        "Monstro", backref="mesa", lazy=True, cascade="all, delete-orphan"
    )

    def __init__(self, nome, mestre_id, descricao=None, sistema="D&D 5E"):
        self.nome = (nome or "").strip()
        self.mestre_id = mestre_id
        self.descricao = descricao
        self.sistema = sistema or "D&D 5E"
        self.codigo_convite = self.gerar_codigo()

    @staticmethod
    def gerar_codigo(tamanho=6):
        """Gera um código de convite alfanumérico aleatório."""
        return "".join(secrets.choice(_ALFABETO_CODIGO) for _ in range(tamanho))

    def tem_membro(self, user_id):
        """Indica se o usuário é membro (jogador) desta mesa."""
        return any(membro.user_id == user_id for membro in self.membros)

    def pode_ver(self, user):
        """Mestre, membro ou ADMIN podem ver a mesa."""
        if user is None:
            return False
        return (
            user.is_admin
            or self.mestre_id == user.id
            or self.tem_membro(user.id)
        )

    def to_dict(self, detalhado=False):
        dados = {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "sistema": self.sistema,
            "codigo_convite": self.codigo_convite,
            "mestre_id": self.mestre_id,
            "mestre_nome": self.mestre.name if self.mestre else None,
            "total_membros": len(self.membros),
        }
        if detalhado:
            dados["membros"] = [membro.to_dict() for membro in self.membros]
            dados["personagens"] = [
                personagem.to_dict(incluir_derivados=False)
                for personagem in self.personagens
            ]
        return dados


class MesaFonteAceita(TimestampMixin, db.Model):
    """Fonte homebrew que o mestre aceitou na sua mesa (fica visível p/ os jogadores)."""

    __tablename__ = "mesa_fontes_aceitas"
    __table_args__ = (
        db.UniqueConstraint("mesa_id", "fonte", name="uq_mesa_fonte"),
    )

    id = db.Column(db.Integer, primary_key=True)
    mesa_id = db.Column(db.Integer, db.ForeignKey("mesas.id"), nullable=False, index=True)
    fonte = db.Column(db.String(120), nullable=False)


class MembroMesa(TimestampMixin, db.Model):
    """Vínculo N:M entre jogador e mesa."""

    __tablename__ = "membros_mesa"
    __table_args__ = (
        db.UniqueConstraint("mesa_id", "user_id", name="uq_membro_mesa"),
    )

    id = db.Column(db.Integer, primary_key=True)
    mesa_id = db.Column(db.Integer, db.ForeignKey("mesas.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    papel_na_mesa = db.Column(db.String(20), default="jogador", nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "nome": self.usuario.name if self.usuario else None,
            "papel_na_mesa": self.papel_na_mesa,
        }
