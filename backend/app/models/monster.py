"""Modelo de Monstro/PDM (bestiário)."""
from app.extensions import db
from app.models.base import TimestampMixin


class Monstro(TimestampMixin, db.Model):
    """
    Criatura do bestiário. `mesa_id` nulo = conteúdo SRD global.
    `is_pdm=True` marca um PDM (NPC) em vez de um monstro genérico.
    """

    __tablename__ = "monstros"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), nullable=True, index=True)
    nome = db.Column(db.String(120), nullable=False)
    tipo = db.Column(db.String(60), nullable=True)
    tamanho = db.Column(db.String(30), nullable=True)
    alinhamento = db.Column(db.String(60), nullable=True)

    ca = db.Column(db.Integer, default=10, nullable=False)
    pv = db.Column(db.Integer, default=1, nullable=False)
    pv_formula = db.Column(db.String(40), nullable=True)
    deslocamento = db.Column(db.String(60), nullable=True)

    atributos = db.Column(db.JSON, default=dict)
    nd = db.Column(db.String(10), nullable=True)
    xp = db.Column(db.Integer, default=0, nullable=False)

    pericias = db.Column(db.Text, nullable=True)
    sentidos = db.Column(db.Text, nullable=True)
    idiomas = db.Column(db.Text, nullable=True)
    habilidades = db.Column(db.JSON, default=list)
    acoes = db.Column(db.JSON, default=list)

    is_pdm = db.Column(db.Boolean, default=False, nullable=False)
    mesa_id = db.Column(db.Integer, db.ForeignKey("mesas.id"), nullable=True, index=True)
    criado_por = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    def pode_editar(self, user, mesa=None):
        """Criador, mestre da mesa de origem ou ADMIN podem editar."""
        if user is None:
            return False
        if user.is_admin or self.criado_por == user.id:
            return True
        if mesa is not None and mesa.mestre_id == user.id:
            return True
        return False

    def to_dict(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "nome": self.nome,
            "tipo": self.tipo,
            "tamanho": self.tamanho,
            "alinhamento": self.alinhamento,
            "ca": self.ca,
            "pv": self.pv,
            "pv_formula": self.pv_formula,
            "deslocamento": self.deslocamento,
            "atributos": self.atributos or {},
            "nd": self.nd,
            "xp": self.xp,
            "pericias": self.pericias,
            "sentidos": self.sentidos,
            "idiomas": self.idiomas,
            "habilidades": self.habilidades or [],
            "acoes": self.acoes or [],
            "is_pdm": self.is_pdm,
            "mesa_id": self.mesa_id,
            "global": self.mesa_id is None,
        }
