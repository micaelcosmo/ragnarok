"""
Modelos de itens: Arma, Armadura e Item (separados, por decisão de design).

- Arma: dano/acerto/propriedades; contribui ataque/dano quando equipada.
- Armadura: define/soma a CA; CA do personagem também tem ajuste manual.
- Item: descritivo apenas (bola de cristal, capa do voo...) — nunca muda número.

Procedência obrigatória (`fonte`) + marcação de `homebrew` (nunca "oficial" sem ser).
Ownership: `personagem_id` (só daquele personagem) | `mesa_id` (homebrew de mesa) | global.
"""
from app.extensions import db
from app.models.base import TimestampMixin


class ConteudoItemMixin(TimestampMixin):
    """Campos comuns aos três tipos de item (procedência + ownership + i18n)."""

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(90), nullable=True, index=True)
    nome = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.Text, nullable=True)

    fonte = db.Column(db.String(120), nullable=False, default="Homebrew")
    homebrew = db.Column(db.Boolean, default=True, nullable=False)
    idioma = db.Column(db.String(2), default="pt")

    criado_por = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    personagem_id = db.Column(db.Integer, db.ForeignKey("personagens.id"), nullable=True, index=True)
    mesa_id = db.Column(db.Integer, db.ForeignKey("mesas.id"), nullable=True, index=True)

    def _base_dict(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "nome": self.nome,
            "descricao": self.descricao,
            "fonte": self.fonte,
            "homebrew": self.homebrew,
            "oficial": not self.homebrew,
            "idioma": self.idioma,
            "criado_por": self.criado_por,
            "personagem_id": self.personagem_id,
            "mesa_id": self.mesa_id,
            "global": self.personagem_id is None and self.mesa_id is None,
        }

    def pode_editar(self, user):
        """Criador, ADMIN ou mestre da mesa de origem podem editar."""
        if user is None:
            return False
        if user.is_admin or self.criado_por == user.id:
            return True
        if self.mesa_id is not None:
            from app.models.campaign import Mesa
            mesa = Mesa.query.get(self.mesa_id)
            if mesa is not None and mesa.mestre_id == user.id:
                return True
        return False


class Arma(ConteudoItemMixin, db.Model):
    __tablename__ = "armas"

    categoria = db.Column(db.String(40), nullable=True)       # simples | marcial
    alcance = db.Column(db.String(40), nullable=True)         # corpo a corpo | à distância
    dano = db.Column(db.String(40), nullable=True)            # ex.: 1d8
    tipo_dano = db.Column(db.String(40), nullable=True)       # cortante | perfurante | concussão
    propriedades = db.Column(db.JSON, default=list)
    bonus_magico = db.Column(db.Integer, default=0)
    efeitos = db.Column(db.JSON, default=dict)

    def to_dict(self):
        dados = self._base_dict()
        dados.update({
            "tipo": "arma",
            "categoria": self.categoria,
            "alcance": self.alcance,
            "dano": self.dano,
            "tipo_dano": self.tipo_dano,
            "propriedades": self.propriedades or [],
            "bonus_magico": self.bonus_magico or 0,
            "efeitos": self.efeitos or {},
        })
        return dados


class Armadura(ConteudoItemMixin, db.Model):
    __tablename__ = "armaduras"

    categoria = db.Column(db.String(40), nullable=True)       # leve | média | pesada | escudo
    ca_base = db.Column(db.Integer, nullable=True)
    ca_soma_des = db.Column(db.Boolean, default=False)
    ca_des_max = db.Column(db.Integer, nullable=True)
    ca_bonus = db.Column(db.Integer, default=0)               # escudo / +X mágico
    requisito_forca = db.Column(db.Integer, default=0)
    furtividade_desvantagem = db.Column(db.Boolean, default=False)
    bonus_magico = db.Column(db.Integer, default=0)
    efeitos = db.Column(db.JSON, default=dict)

    def to_dict(self):
        dados = self._base_dict()
        dados.update({
            "tipo": "armadura",
            "categoria": self.categoria,
            "ca_base": self.ca_base,
            "ca_soma_des": self.ca_soma_des,
            "ca_des_max": self.ca_des_max,
            "ca_bonus": self.ca_bonus or 0,
            "requisito_forca": self.requisito_forca or 0,
            "furtividade_desvantagem": self.furtividade_desvantagem,
            "bonus_magico": self.bonus_magico or 0,
            "efeitos": self.efeitos or {},
        })
        return dados


class Item(ConteudoItemMixin, db.Model):
    """Item maravilhoso/poção/etc. — apenas descritivo (sem efeito numérico)."""

    __tablename__ = "itens"

    tipo_item = db.Column(db.String(60), nullable=True)       # maravilhoso, poção, anel...
    raridade = db.Column(db.String(40), nullable=True)
    requer_sintonia = db.Column(db.Boolean, default=False)

    def to_dict(self):
        dados = self._base_dict()
        dados.update({
            "tipo": "item",
            "tipo_item": self.tipo_item,
            "raridade": self.raridade,
            "requer_sintonia": self.requer_sintonia,
        })
        return dados
