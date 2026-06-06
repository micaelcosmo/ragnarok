"""
Popula o banco com o conteúdo SRD e cria o usuário ADMIN inicial.

Uso: ``python -m app.seed``  (idempotente — pode rodar várias vezes).
Orientado a objetos: a classe SeedRunner encapsula o carregamento dos JSON
e a persistência idempotente de cada catálogo.
"""
import json
import secrets
from pathlib import Path

from app import create_app
from app.extensions import db
from app.models.reference import Antecedente, Classe, Magia, Raca, Talento
from app.models.monster import Monstro
from app.models.items import Item
from app.models.user import User

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class SeedRunner:
    """Executa o seed do catálogo SRD e do admin inicial."""

    def __init__(self, app):
        self.app = app
        self.resumo = {}

    def _carregar_json(self, nome_arquivo):
        caminho = DATA_DIR / nome_arquivo
        if not caminho.exists():
            print(f"[seed] aviso: {nome_arquivo} não encontrado, pulando.")
            return []
        with caminho.open(encoding="utf-8") as arquivo:
            return json.load(arquivo)

    def _upsert(self, modelo, registros, campos):
        """Insere registros ausentes (por slug). Não sobrescreve existentes."""
        inseridos = 0
        for registro in registros:
            slug = registro.get("slug")
            if slug and modelo.query.filter_by(slug=slug).first():
                continue
            dados = {campo: registro.get(campo) for campo in campos if campo in registro}
            db.session.add(modelo(**dados))
            inseridos += 1
        db.session.commit()
        self.resumo[modelo.__tablename__] = inseridos
        return inseridos

    def semear_admin(self):
        config = self.app.config
        email = config["SEED_ADMIN_EMAIL"].lower()
        if User.query.filter_by(email=email).first():
            self.resumo["admin"] = "já existia"
            return
        # Sem senha definida no ambiente: gera uma aleatória e avisa (nunca usa default fraco).
        senha = config.get("SEED_ADMIN_PASSWORD")
        gerada = False
        if not senha:
            senha = secrets.token_urlsafe(12)
            gerada = True
        admin = User(
            email=email,
            name=config["SEED_ADMIN_NAME"],
            password=senha,
            role="ADMIN",
        )
        db.session.add(admin)
        db.session.commit()
        if gerada:
            print("=" * 60)
            print(f"[seed] ADMIN criado: {email}")
            print(f"[seed] SENHA GERADA (anote!): {senha}")
            print("[seed] Defina SEED_ADMIN_PASSWORD no .env para escolher a sua.")
            print("=" * 60)
            self.resumo["admin"] = f"criado ({email}) — senha gerada (ver log)"
        else:
            self.resumo["admin"] = f"criado ({email})"

    def semear_demo(self):
        """Cria contas demo (MESTRE e JOGADOR) para facilitar os testes."""
        demos = [
            ("mestre@ragnarok.local", "Mestre Demo", "mestre123", "MESTRE"),
            ("jogador@ragnarok.local", "Jogador Demo", "jogador123", "JOGADOR"),
        ]
        criados = 0
        for email, nome, senha, papel in demos:
            if User.query.filter_by(email=email).first():
                continue
            db.session.add(User(email=email, name=nome, password=senha, role=papel))
            criados += 1
        db.session.commit()
        self.resumo["demo"] = f"{criados} conta(s) demo"

    def semear_racas(self):
        campos = ["slug", "nome", "descricao", "deslocamento", "tamanho",
                  "bonus_atributos", "tracos", "subracas", "efeitos"]
        registros = self._carregar_json("races.json")
        for registro in registros:
            # Raça concede bônus de atributo automaticamente (efeito).
            registro.setdefault("efeitos", {})
            registro["efeitos"].setdefault("atributos", registro.get("bonus_atributos") or {})
        self._upsert(Raca, registros, campos)

    def semear_classes(self):
        campos = ["slug", "nome", "descricao", "dado_vida", "atributo_principal",
                  "salvaguardas", "pericias_disponiveis", "num_pericias",
                  "conjurador", "atributo_conjuracao", "proficiencias_armadura",
                  "proficiencias_arma", "efeitos"]
        registros = self._carregar_json("classes.json")
        for registro in registros:
            # Classe concede proficiência nas salvaguardas automaticamente.
            registro.setdefault("efeitos", {})
            registro["efeitos"].setdefault("salvaguardas", registro.get("salvaguardas") or [])
        self._upsert(Classe, registros, campos)

    def semear_antecedentes(self):
        campos = ["slug", "nome", "descricao", "pericias", "idiomas", "equipamento", "efeitos"]
        registros = self._carregar_json("backgrounds.json")
        for registro in registros:
            # Antecedente concede proficiência nas perícias automaticamente.
            registro.setdefault("efeitos", {})
            registro["efeitos"].setdefault("pericias", registro.get("pericias") or [])
        self._upsert(Antecedente, registros, campos)

    def semear_magias(self):
        campos = ["slug", "nome", "nivel", "escola", "tempo_conjuracao", "alcance",
                  "componentes", "duracao", "concentracao", "ritual", "classes", "descricao"]
        self._upsert(Magia, self._carregar_json("spells.json"), campos)

    def semear_monstros(self):
        campos = ["slug", "nome", "tipo", "tamanho", "alinhamento", "ca", "pv",
                  "pv_formula", "deslocamento", "atributos", "nd", "xp", "pericias",
                  "sentidos", "idiomas", "habilidades", "acoes"]
        self._upsert(Monstro, self._carregar_json("monsters.json"), campos)

    def semear_talentos(self):
        campos = ["slug", "nome", "descricao", "pre_requisito", "fonte", "efeitos"]
        self._upsert(Talento, self._carregar_json("feats.json"), campos)

    def semear_equipamento(self):
        """Equipamento mundano do SRD (gear + pacotes) como Itens globais oficiais."""
        campos = ["slug", "nome", "descricao", "tipo_item", "fonte", "homebrew", "idioma"]
        registros = self._carregar_json("gear.json")
        for registro in registros:
            registro.setdefault("homebrew", False)
            registro.setdefault("idioma", "pt")
        self._upsert(Item, registros, campos)

    def backfill_efeitos(self):
        """
        Preenche `efeitos` em conteúdo de referência JÁ EXISTENTE que ainda não tem
        (ex.: seedado/ingerido antes da feature de efeitos). Idempotente: só toca em vazios.
        """
        preenchidos = 0
        for raca in Raca.query.all():
            if not raca.efeitos and raca.bonus_atributos:
                raca.efeitos = {"atributos": raca.bonus_atributos}
                preenchidos += 1
        for classe in Classe.query.all():
            if not classe.efeitos and classe.salvaguardas:
                classe.efeitos = {"salvaguardas": classe.salvaguardas}
                preenchidos += 1
        for antecedente in Antecedente.query.all():
            if not antecedente.efeitos and antecedente.pericias:
                antecedente.efeitos = {"pericias": antecedente.pericias}
                preenchidos += 1
        db.session.commit()
        self.resumo["backfill_efeitos"] = preenchidos

    def executar(self):
        with self.app.app_context():
            db.create_all()
            self.semear_admin()
            self.semear_demo()
            self.semear_racas()
            self.semear_classes()
            self.semear_antecedentes()
            self.semear_magias()
            self.semear_monstros()
            self.semear_talentos()
            self.semear_equipamento()
            self.backfill_efeitos()
        return self.resumo


def main():
    app = create_app()
    resumo = SeedRunner(app).executar()
    print("[seed] concluído:")
    for chave, valor in resumo.items():
        print(f"  - {chave}: {valor}")


if __name__ == "__main__":
    main()
