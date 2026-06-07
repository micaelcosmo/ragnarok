"""Modelo de Personagem (ficha completa de D&D 5E)."""
from app.extensions import db
from app.models.base import TimestampMixin


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
    ca_ajuste = db.Column(db.Integer, default=0, nullable=False)  # ajuste manual de CA (+/-)
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

    # Fontes de efeitos (bônus reversíveis): talentos escolhidos (slugs).
    talentos = db.Column(db.JSON, default=list)
    # Traços/recursos personalizados do personagem: [{nome, descricao, fonte, efeitos:{...}}].
    # Sem `efeitos` = descritivo; com `efeitos` = incremental (soma na ficha, reversível).
    tracos_extras = db.Column(db.JSON, default=list)
    # Aumentos de Habilidade (ASI) alocados manualmente: {for..car: int}. Pool reversível (E26).
    bonus_atributos_manuais = db.Column(db.JSON, default=dict)
    # Recursos de classe com usos: [{nome, max, atual, recarga, descricao}]. Recarrega por descanso (E27).
    recursos = db.Column(db.JSON, default=list)

    # Equipamento ativo (fontes de efeitos de itens).
    armadura_equipada_id = db.Column(db.Integer, db.ForeignKey("armaduras.id"), nullable=True)
    armas_equipadas = db.Column(db.JSON, default=list)   # lista de ids de Arma

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
    avatar_url = db.Column(db.String(300), nullable=True)  # retrato do personagem

    # Identidade / aparência (página 2 da ficha oficial)
    idade = db.Column(db.String(40), nullable=True)
    altura = db.Column(db.String(40), nullable=True)
    peso = db.Column(db.String(40), nullable=True)
    olhos = db.Column(db.String(40), nullable=True)
    pele = db.Column(db.String(40), nullable=True)
    cabelo = db.Column(db.String(40), nullable=True)
    faccao = db.Column(db.String(120), nullable=True)
    aparencia = db.Column(db.Text, nullable=True)
    aliados = db.Column(db.Text, nullable=True)
    tesouro = db.Column(db.Text, nullable=True)
    simbolo_faccao_url = db.Column(db.String(300), nullable=True)

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
        """
        Bloco de campos calculados, já com os efeitos das fontes (raça/classe/antecedente/
        talentos) aplicados sobre a camada base. Ver ConstrutorDeFicha.
        """
        # Import tardio para evitar import circular (service -> models).
        from app.services.construtor import construir_derivados

        return construir_derivados(self)

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
            "ca_ajuste": self.ca_ajuste,
            "iniciativa_bonus": self.iniciativa_bonus,
            "deslocamento": self.deslocamento,
            "pv_max": self.pv_max,
            "pv_atual": self.pv_atual,
            "pv_temp": self.pv_temp,
            "dado_vida": self.dado_vida,
            "inspiracao": self.inspiracao,
            "pericias_proficientes": self.pericias_proficientes or [],
            "salvaguardas_proficientes": self.salvaguardas_proficientes or [],
            "talentos": self.talentos or [],
            "tracos_extras": self.tracos_extras or [],
            "bonus_atributos_manuais": self.bonus_atributos_manuais or {},
            "recursos": self.recursos or [],
            "armadura_equipada_id": self.armadura_equipada_id,
            "armas_equipadas": self.armas_equipadas or [],
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
            "idade": self.idade,
            "altura": self.altura,
            "peso": self.peso,
            "olhos": self.olhos,
            "pele": self.pele,
            "cabelo": self.cabelo,
            "faccao": self.faccao,
            "aparencia": self.aparencia,
            "aliados": self.aliados,
            "tesouro": self.tesouro,
            "simbolo_faccao_url": self.simbolo_faccao_url,
        }
        if incluir_derivados:
            dados["derivados"] = self.derivados()
        return dados
