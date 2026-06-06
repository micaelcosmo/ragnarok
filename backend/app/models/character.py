"""Modelo de Personagem (ficha completa de D&D 5E)."""
from app.extensions import db
from app.models.base import TimestampMixin
from app.rules import dnd5e


class Personagem(TimestampMixin, db.Model):
    """Ficha de personagem 5E. Os campos derivados são calculados na serialização."""

    __tablename__ = "personagens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    mesa_id = db.Column(db.Integer, db.ForeignKey("mesas.id"), nullable=True, index=True)

    # Identidade
    nome = db.Column(db.String(120), nullable=False)
    nome_jogador = db.Column(db.String(120), nullable=True)
    raca_slug = db.Column(db.String(60), nullable=True)
    classe_slug = db.Column(db.String(60), nullable=True)
    antecedente_slug = db.Column(db.String(60), nullable=True)
    tendencia = db.Column(db.String(40), nullable=True)
    nivel = db.Column(db.Integer, default=1, nullable=False)
    xp = db.Column(db.Integer, default=0, nullable=False)

    # Atributos base (1..30)
    forca = db.Column(db.Integer, default=10, nullable=False)
    destreza = db.Column(db.Integer, default=10, nullable=False)
    constituicao = db.Column(db.Integer, default=10, nullable=False)
    inteligencia = db.Column(db.Integer, default=10, nullable=False)
    sabedoria = db.Column(db.Integer, default=10, nullable=False)
    carisma = db.Column(db.Integer, default=10, nullable=False)

    # Combate
    ca = db.Column(db.Integer, default=10, nullable=False)
    iniciativa_bonus = db.Column(db.Integer, default=0, nullable=False)
    deslocamento = db.Column(db.String(20), default="9 m", nullable=True)
    pv_max = db.Column(db.Integer, default=1, nullable=False)
    pv_atual = db.Column(db.Integer, default=1, nullable=False)
    pv_temp = db.Column(db.Integer, default=0, nullable=False)
    dado_vida = db.Column(db.String(20), default="1d8", nullable=True)
    inspiracao = db.Column(db.Boolean, default=False, nullable=False)

    # Proficiências (listas)
    pericias_proficientes = db.Column(db.JSON, default=list)
    salvaguardas_proficientes = db.Column(db.JSON, default=list)
    outras_proficiencias = db.Column(db.Text, nullable=True)

    # Magia
    classe_conjuradora = db.Column(db.String(60), nullable=True)
    atributo_conjuracao = db.Column(db.String(3), nullable=True)
    truques = db.Column(db.JSON, default=list)
    magias = db.Column(db.JSON, default=list)

    # Texto livre / roleplay
    tracos_personalidade = db.Column(db.Text, nullable=True)
    ideais = db.Column(db.Text, nullable=True)
    vinculos = db.Column(db.Text, nullable=True)
    fraquezas = db.Column(db.Text, nullable=True)
    historia = db.Column(db.Text, nullable=True)
    caracteristicas = db.Column(db.Text, nullable=True)
    idiomas = db.Column(db.Text, nullable=True)
    equipamento = db.Column(db.Text, nullable=True)
    ataques = db.Column(db.Text, nullable=True)
    dinheiro = db.Column(db.String(120), nullable=True)
    avatar_url = db.Column(db.String(300), nullable=True)

    ATRIBUTOS_COLUNAS = {
        "for": "forca",
        "des": "destreza",
        "con": "constituicao",
        "int": "inteligencia",
        "sab": "sabedoria",
        "car": "carisma",
    }

    def atributos_dict(self):
        """Atributos no formato {for, des, con, int, sab, car}."""
        return {
            chave: getattr(self, coluna)
            for chave, coluna in self.ATRIBUTOS_COLUNAS.items()
        }

    def derivados(self):
        """Bloco de campos calculados (modificadores, perícias, salvaguardas, etc.)."""
        return dnd5e.ficha_derivada(
            self.atributos_dict(),
            self.nivel,
            pericias_proficientes=self.pericias_proficientes or [],
            salvaguardas_proficientes=self.salvaguardas_proficientes or [],
            atributo_conjuracao=self.atributo_conjuracao,
            iniciativa_bonus_extra=self.iniciativa_bonus or 0,
        )

    def to_dict(self, incluir_derivados=True):
        """Serializa a ficha; inclui o bloco `derivados` por padrão."""
        dados = {
            "id": self.id,
            "user_id": self.user_id,
            "mesa_id": self.mesa_id,
            "nome": self.nome,
            "nome_jogador": self.nome_jogador,
            "raca_slug": self.raca_slug,
            "classe_slug": self.classe_slug,
            "antecedente_slug": self.antecedente_slug,
            "tendencia": self.tendencia,
            "nivel": self.nivel,
            "xp": self.xp,
            "atributos": self.atributos_dict(),
            "ca": self.ca,
            "iniciativa_bonus": self.iniciativa_bonus,
            "deslocamento": self.deslocamento,
            "pv_max": self.pv_max,
            "pv_atual": self.pv_atual,
            "pv_temp": self.pv_temp,
            "dado_vida": self.dado_vida,
            "inspiracao": self.inspiracao,
            "pericias_proficientes": self.pericias_proficientes or [],
            "salvaguardas_proficientes": self.salvaguardas_proficientes or [],
            "outras_proficiencias": self.outras_proficiencias,
            "classe_conjuradora": self.classe_conjuradora,
            "atributo_conjuracao": self.atributo_conjuracao,
            "truques": self.truques or [],
            "magias": self.magias or [],
            "tracos_personalidade": self.tracos_personalidade,
            "ideais": self.ideais,
            "vinculos": self.vinculos,
            "fraquezas": self.fraquezas,
            "historia": self.historia,
            "caracteristicas": self.caracteristicas,
            "idiomas": self.idiomas,
            "equipamento": self.equipamento,
            "ataques": self.ataques,
            "dinheiro": self.dinheiro,
            "avatar_url": self.avatar_url,
        }
        if incluir_derivados:
            dados["derivados"] = self.derivados()
        return dados
