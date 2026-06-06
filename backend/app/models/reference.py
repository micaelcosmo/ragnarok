"""Modelos de conteúdo de referência (raças, classes, antecedentes, magias, talentos).

Todos carregam o campo `fonte` (livro/origem) para rastreabilidade e filtro por procedência.
"""
from app.extensions import db

FONTE_PADRAO = "SRD 5.1"


class Raca(db.Model):
    """Raça jogável, com possíveis sub-raças."""

    __tablename__ = "racas"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(60), unique=True, nullable=False, index=True)
    nome = db.Column(db.String(80), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    deslocamento = db.Column(db.Integer, default=9)
    tamanho = db.Column(db.String(30), nullable=True)
    bonus_atributos = db.Column(db.JSON, default=dict)
    tracos = db.Column(db.JSON, default=list)
    subracas = db.Column(db.JSON, default=list)
    fonte = db.Column(db.String(120), default=FONTE_PADRAO, index=True)
    efeitos = db.Column(db.JSON, default=dict)

    def to_dict(self):
        return {
            "slug": self.slug,
            "nome": self.nome,
            "descricao": self.descricao,
            "deslocamento": self.deslocamento,
            "tamanho": self.tamanho,
            "bonus_atributos": self.bonus_atributos or {},
            "tracos": self.tracos or [],
            "subracas": self.subracas or [],
            "fonte": self.fonte,
            "efeitos": self.efeitos or {},
        }


class Classe(db.Model):
    """Classe de personagem do SRD."""

    __tablename__ = "classes"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(60), unique=True, nullable=False, index=True)
    nome = db.Column(db.String(80), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    dado_vida = db.Column(db.Integer, default=8)
    atributo_principal = db.Column(db.JSON, default=list)
    salvaguardas = db.Column(db.JSON, default=list)
    pericias_disponiveis = db.Column(db.JSON, default=list)
    num_pericias = db.Column(db.Integer, default=2)
    conjurador = db.Column(db.Boolean, default=False)
    atributo_conjuracao = db.Column(db.String(3), nullable=True)
    proficiencias_armadura = db.Column(db.JSON, default=list)
    proficiencias_arma = db.Column(db.JSON, default=list)
    fonte = db.Column(db.String(120), default=FONTE_PADRAO, index=True)
    efeitos = db.Column(db.JSON, default=dict)

    def to_dict(self):
        return {
            "slug": self.slug,
            "nome": self.nome,
            "descricao": self.descricao,
            "dado_vida": self.dado_vida,
            "atributo_principal": self.atributo_principal or [],
            "salvaguardas": self.salvaguardas or [],
            "pericias_disponiveis": self.pericias_disponiveis or [],
            "num_pericias": self.num_pericias,
            "conjurador": self.conjurador,
            "atributo_conjuracao": self.atributo_conjuracao,
            "proficiencias_armadura": self.proficiencias_armadura or [],
            "proficiencias_arma": self.proficiencias_arma or [],
            "fonte": self.fonte,
            "efeitos": self.efeitos or {},
        }


class Antecedente(db.Model):
    """Antecedente (background) do SRD."""

    __tablename__ = "antecedentes"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(60), unique=True, nullable=False, index=True)
    nome = db.Column(db.String(80), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    pericias = db.Column(db.JSON, default=list)
    idiomas = db.Column(db.Integer, default=0)
    equipamento = db.Column(db.Text, nullable=True)
    fonte = db.Column(db.String(120), default=FONTE_PADRAO, index=True)
    efeitos = db.Column(db.JSON, default=dict)

    def to_dict(self):
        return {
            "slug": self.slug,
            "nome": self.nome,
            "descricao": self.descricao,
            "pericias": self.pericias or [],
            "idiomas": self.idiomas,
            "equipamento": self.equipamento,
            "fonte": self.fonte,
            "efeitos": self.efeitos or {},
        }


class Magia(db.Model):
    """Magia do SRD."""

    __tablename__ = "magias"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), unique=True, nullable=False, index=True)
    nome = db.Column(db.String(120), nullable=False)
    nivel = db.Column(db.Integer, default=0, index=True)
    escola = db.Column(db.String(40), nullable=True)
    tempo_conjuracao = db.Column(db.String(60), nullable=True)
    alcance = db.Column(db.String(60), nullable=True)
    componentes = db.Column(db.String(60), nullable=True)
    duracao = db.Column(db.String(60), nullable=True)
    concentracao = db.Column(db.Boolean, default=False)
    ritual = db.Column(db.Boolean, default=False)
    classes = db.Column(db.JSON, default=list)
    descricao = db.Column(db.Text, nullable=True)
    fonte = db.Column(db.String(120), default=FONTE_PADRAO, index=True)

    def to_dict(self):
        return {
            "slug": self.slug,
            "nome": self.nome,
            "nivel": self.nivel,
            "escola": self.escola,
            "tempo_conjuracao": self.tempo_conjuracao,
            "alcance": self.alcance,
            "componentes": self.componentes,
            "duracao": self.duracao,
            "concentracao": self.concentracao,
            "ritual": self.ritual,
            "classes": self.classes or [],
            "descricao": self.descricao,
            "fonte": self.fonte,
        }


class Talento(db.Model):
    """Talento (feat). Em geral vem do pipeline de conteúdo (o SRD só traz 'Grappler')."""

    __tablename__ = "talentos"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), unique=True, nullable=False, index=True)
    nome = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    pre_requisito = db.Column(db.String(160), nullable=True)
    fonte = db.Column(db.String(120), default=FONTE_PADRAO, index=True)
    efeitos = db.Column(db.JSON, default=dict)

    def to_dict(self):
        return {
            "slug": self.slug,
            "nome": self.nome,
            "descricao": self.descricao,
            "pre_requisito": self.pre_requisito,
            "fonte": self.fonte,
            "efeitos": self.efeitos or {},
        }
