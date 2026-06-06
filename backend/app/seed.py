"""
Popula o banco com o conteúdo SRD e cria o usuário ADMIN inicial.

Uso: ``python -m app.seed``  (idempotente — pode rodar várias vezes).
Orientado a objetos: a classe SeedRunner encapsula o carregamento dos JSON
e a persistência idempotente de cada catálogo.
"""
import json
from pathlib import Path

from app import create_app
from app.extensions import db
from app.models.reference import Antecedente, Classe, Magia, Raca, Talento
from app.models.monster import Monstro
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
        admin = User(
            email=email,
            name=config["SEED_ADMIN_NAME"],
            password=config["SEED_ADMIN_PASSWORD"],
            role="ADMIN",
        )
        db.session.add(admin)
        db.session.commit()
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
                  "bonus_atributos", "tracos", "subracas"]
        self._upsert(Raca, self._carregar_json("races.json"), campos)

    def semear_classes(self):
        campos = ["slug", "nome", "descricao", "dado_vida", "atributo_principal",
                  "salvaguardas", "pericias_disponiveis", "num_pericias",
                  "conjurador", "atributo_conjuracao", "proficiencias_armadura",
                  "proficiencias_arma"]
        self._upsert(Classe, self._carregar_json("classes.json"), campos)

    def semear_antecedentes(self):
        campos = ["slug", "nome", "descricao", "pericias", "idiomas", "equipamento"]
        self._upsert(Antecedente, self._carregar_json("backgrounds.json"), campos)

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
        campos = ["slug", "nome", "descricao", "pre_requisito", "fonte"]
        self._upsert(Talento, self._carregar_json("feats.json"), campos)

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
        return self.resumo


def main():
    app = create_app()
    resumo = SeedRunner(app).executar()
    print("[seed] concluído:")
    for chave, valor in resumo.items():
        print(f"  - {chave}: {valor}")


if __name__ == "__main__":
    main()
