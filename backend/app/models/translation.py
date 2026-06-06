"""Cache de traduções (en->pt). Traduz uma vez e guarda; idioma pt-nativo não precisa."""
from app.extensions import db
from app.models.base import TimestampMixin


class Traducao(TimestampMixin, db.Model):
    """Tradução cacheada de um campo de um registro de conteúdo."""

    __tablename__ = "traducoes"
    __table_args__ = (
        db.UniqueConstraint("tipo", "slug", "campo", "idioma", name="uq_traducao"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(30), nullable=False)      # spells, races, ...
    slug = db.Column(db.String(90), nullable=False, index=True)
    campo = db.Column(db.String(30), nullable=False)     # nome, descricao
    idioma = db.Column(db.String(2), default="pt", nullable=False)
    texto = db.Column(db.Text, nullable=False)
