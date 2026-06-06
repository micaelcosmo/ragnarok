"""Endpoints de conteúdo de referência (catálogo SRD). Leitura: autenticado; escrita: ADMIN."""
from flask import Blueprint, request

from app.extensions import db
from app.models.reference import Antecedente, Classe, Magia, Raca, Talento
from app.utils.auth import auth_required, role_required
from app.utils.errors import Conflict, NotFound
from app.utils.responses import corpo_json, created, ok

bp = Blueprint("reference", __name__)


def _filtrar_fonte(consulta, modelo):
    """Aplica o filtro opcional ?fonte= (procedência/livro)."""
    fonte = request.args.get("fonte")
    if fonte:
        consulta = consulta.filter(modelo.fonte == fonte)
    return consulta


@bp.get("/reference/races")
@auth_required
def listar_racas():
    racas = _filtrar_fonte(Raca.query, Raca).order_by(Raca.nome).all()
    return ok([raca.to_dict() for raca in racas], meta={"total": len(racas)})


@bp.get("/reference/races/<slug>")
@auth_required
def obter_raca(slug):
    raca = Raca.query.filter_by(slug=slug).first()
    if raca is None:
        raise NotFound("Raça não encontrada.")
    return ok(raca.to_dict())


@bp.get("/reference/classes")
@auth_required
def listar_classes():
    classes = _filtrar_fonte(Classe.query, Classe).order_by(Classe.nome).all()
    return ok([classe.to_dict() for classe in classes], meta={"total": len(classes)})


@bp.get("/reference/classes/<slug>")
@auth_required
def obter_classe(slug):
    classe = Classe.query.filter_by(slug=slug).first()
    if classe is None:
        raise NotFound("Classe não encontrada.")
    return ok(classe.to_dict())


@bp.get("/reference/backgrounds")
@auth_required
def listar_antecedentes():
    antecedentes = _filtrar_fonte(Antecedente.query, Antecedente).order_by(Antecedente.nome).all()
    return ok(
        [antecedente.to_dict() for antecedente in antecedentes],
        meta={"total": len(antecedentes)},
    )


@bp.get("/reference/feats")
@auth_required
def listar_talentos():
    """Lista talentos (feats), com filtros opcionais ?q= e ?fonte=."""
    consulta = _filtrar_fonte(Talento.query, Talento)
    busca = request.args.get("q")
    if busca:
        consulta = consulta.filter(Talento.nome.ilike(f"%{busca}%"))
    talentos = consulta.order_by(Talento.nome).all()
    return ok([talento.to_dict() for talento in talentos], meta={"total": len(talentos)})


@bp.get("/reference/feats/<slug>")
@auth_required
def obter_talento(slug):
    talento = Talento.query.filter_by(slug=slug).first()
    if talento is None:
        raise NotFound("Talento não encontrado.")
    return ok(talento.to_dict())


@bp.get("/reference/sources")
@auth_required
def listar_fontes():
    """Lista as fontes/livros presentes no catálogo (para filtros na UI)."""
    fontes = set()
    for modelo in (Raca, Classe, Antecedente, Magia, Talento):
        for (valor,) in db.session.query(modelo.fonte).distinct().all():
            if valor:
                fontes.add(valor)
    return ok(sorted(fontes))


@bp.get("/reference/spells")
@auth_required
def listar_magias():
    consulta = _filtrar_fonte(Magia.query, Magia)
    nivel = request.args.get("nivel")
    classe = request.args.get("classe")
    busca = request.args.get("q")

    if nivel is not None and nivel != "":
        consulta = consulta.filter(Magia.nivel == int(nivel))
    if busca:
        consulta = consulta.filter(Magia.nome.ilike(f"%{busca}%"))

    consulta = consulta.order_by(Magia.nivel, Magia.nome)
    total = consulta.count()
    limite = min(max(int(request.args.get("limit", 80)), 1), 500)
    magias = consulta.limit(limite if not classe else 500).all()
    if classe:
        magias = [magia for magia in magias if classe in (magia.classes or [])][:limite]

    return ok(
        [magia.to_dict() for magia in magias],
        meta={"total": total, "exibidos": len(magias), "limite": limite},
    )


@bp.get("/reference/spells/<slug>")
@auth_required
def obter_magia(slug):
    magia = Magia.query.filter_by(slug=slug).first()
    if magia is None:
        raise NotFound("Magia não encontrada.")
    return ok(magia.to_dict())


# ---- Escrita (somente ADMIN) — exemplo para magias (compêndio editável) ----

@bp.post("/reference/spells")
@role_required("ADMIN")
def criar_magia():
    dados = corpo_json(["slug", "nome"])
    if Magia.query.filter_by(slug=dados["slug"]).first():
        raise Conflict("Já existe magia com esse slug.")
    magia = Magia(**_campos_magia(dados))
    db.session.add(magia)
    db.session.commit()
    return created(magia.to_dict())


@bp.delete("/reference/spells/<slug>")
@role_required("ADMIN")
def remover_magia(slug):
    magia = Magia.query.filter_by(slug=slug).first()
    if magia is None:
        raise NotFound("Magia não encontrada.")
    db.session.delete(magia)
    db.session.commit()
    return ok({"removido": slug})


def _campos_magia(dados):
    permitidos = (
        "slug", "nome", "nivel", "escola", "tempo_conjuracao", "alcance",
        "componentes", "duracao", "concentracao", "ritual", "classes", "descricao",
    )
    return {campo: dados[campo] for campo in permitidos if campo in dados}
