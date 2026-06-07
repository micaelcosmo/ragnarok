"""Endpoints de conteúdo de referência (catálogo SRD). Leitura: autenticado; escrita: ADMIN."""
from flask import Blueprint, request

from app.extensions import db
from app.models.items import Arma, Armadura, Item
from app.models.reference import Antecedente, Classe, Magia, Raca, Talento
from app.utils.auth import auth_required, current_user, role_required
from app.utils.errors import Conflict, Forbidden, NotFound
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


def _listar_itens(modelo):
    """Lista o catálogo GLOBAL (SRD/OGL) de um tipo de item, com ?q=, ?fonte= e paginação."""
    consulta = modelo.query.filter(modelo.personagem_id.is_(None), modelo.mesa_id.is_(None))
    consulta = _filtrar_fonte(consulta, modelo)
    busca = request.args.get("q")
    if busca:
        consulta = consulta.filter(modelo.nome.ilike(f"%{busca}%"))
    consulta = consulta.order_by(modelo.nome)
    total = consulta.count()
    limite = min(max(int(request.args.get("limit", 80)), 1), 500)
    registros = consulta.limit(limite).all()
    dados = [r.to_dict() for r in registros]

    # Tradução opcional (?idioma=pt) para conteúdo importado em inglês.
    if request.args.get("idioma") == "pt":
        from app.services.tradutor import Tradutor
        tradutor = Tradutor("pt")
        tipo_rota = {"Arma": "weapons", "Armadura": "armor", "Item": "items"}.get(modelo.__name__, "")
        dados = [tradutor.aplicar(tipo_rota, d) for d in dados]

    return ok(dados, meta={"total": total, "exibidos": len(registros), "limite": limite})


@bp.get("/reference/weapons")
@auth_required
def listar_armas():
    return _listar_itens(Arma)


@bp.get("/reference/armor")
@auth_required
def listar_armaduras():
    return _listar_itens(Armadura)


@bp.get("/reference/items")
@auth_required
def listar_itens_magicos():
    return _listar_itens(Item)


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


# ============================================================================
# Escrita do compêndio — MESTRE + ADMIN. Fonte OBRIGATÓRIA; conteúdo criado na UI
# é sempre HOMEBREW (nunca "oficial"). Editar um oficial cria uma CÓPIA homebrew.
# ============================================================================

# tipo de rota -> (Model, campos editáveis)
_TIPOS_REF = {
    "races": (Raca, ["slug", "nome", "descricao", "deslocamento", "tamanho",
                     "bonus_atributos", "tracos", "subracas", "efeitos"]),
    "classes": (Classe, ["slug", "nome", "descricao", "dado_vida", "atributo_principal",
                        "salvaguardas", "pericias_disponiveis", "num_pericias",
                        "conjurador", "atributo_conjuracao", "efeitos"]),
    "backgrounds": (Antecedente, ["slug", "nome", "descricao", "pericias", "idiomas",
                                 "equipamento", "efeitos"]),
    "feats": (Talento, ["slug", "nome", "descricao", "pre_requisito", "efeitos"]),
    "spells": (Magia, ["slug", "nome", "nivel", "escola", "tempo_conjuracao", "alcance",
                      "componentes", "duracao", "concentracao", "ritual", "classes", "descricao"]),
}


def _modelo_ref(tipo):
    if tipo not in _TIPOS_REF:
        raise NotFound("Tipo de conteúdo inválido.")
    return _TIPOS_REF[tipo]


@bp.post("/reference/<tipo>")
@role_required("MESTRE")
def criar_referencia(tipo):
    """Cria conteúdo homebrew no compêndio (MESTRE/ADMIN). `fonte` é obrigatória."""
    modelo, campos = _modelo_ref(tipo)
    dados = corpo_json(["slug", "nome", "fonte"])
    if modelo.query.filter_by(slug=dados["slug"]).first():
        raise Conflict("Já existe conteúdo com esse slug.")
    registro = modelo(**{campo: dados[campo] for campo in campos if campo in dados})
    registro.fonte = dados["fonte"]
    registro.homebrew = True
    registro.criado_por = current_user().id
    db.session.add(registro)
    db.session.commit()
    return created(registro.to_dict())


@bp.put("/reference/<tipo>/<slug>")
@role_required("MESTRE")
def atualizar_referencia(tipo, slug):
    """
    Edita conteúdo. Editar um item OFICIAL cria uma CÓPIA homebrew (preserva a procedência);
    editar homebrew altera no lugar.
    """
    modelo, campos = _modelo_ref(tipo)
    registro = modelo.query.filter_by(slug=slug).first()
    if registro is None:
        raise NotFound("Conteúdo não encontrado.")
    dados = corpo_json()

    if not registro.homebrew:
        # Não corrompe o oficial: cria variante homebrew.
        novo = modelo(**{campo: getattr(registro, campo) for campo in campos
                        if hasattr(registro, campo)})
        novo.slug = dados.get("slug") or f"{slug}-homebrew-{current_user().id}"
        if modelo.query.filter_by(slug=novo.slug).first():
            raise Conflict("Já existe uma variante com esse slug.")
        for campo in campos:
            if campo in dados:
                setattr(novo, campo, dados[campo])
        novo.homebrew = True
        novo.criado_por = current_user().id
        novo.fonte = dados.get("fonte") or f"Homebrew — {current_user().name}"
        db.session.add(novo)
        db.session.commit()
        return created(novo.to_dict())

    for campo in campos:
        if campo in dados:
            setattr(registro, campo, dados[campo])
    if dados.get("fonte"):
        registro.fonte = dados["fonte"]
    db.session.commit()
    return ok(registro.to_dict())


@bp.post("/reference/<tipo>/<slug>/oficializar")
@role_required("ADMIN")
def oficializar_referencia(tipo, slug):
    """ADMIN promove um conteúdo a OFICIAL (homebrew=False). `fonte` opcional. Idempotente."""
    modelo, _campos = _modelo_ref(tipo)
    registro = modelo.query.filter_by(slug=slug).first()
    if registro is None:
        raise NotFound("Conteúdo não encontrado.")
    dados = corpo_json()
    registro.homebrew = False
    if dados.get("fonte"):
        registro.fonte = dados["fonte"]
    db.session.commit()
    return ok(registro.to_dict())


@bp.delete("/reference/<tipo>/<slug>")
@role_required("MESTRE")
def remover_referencia(tipo, slug):
    """Remove conteúdo. Mestre só remove homebrew; ADMIN remove qualquer um."""
    modelo, _campos = _modelo_ref(tipo)
    registro = modelo.query.filter_by(slug=slug).first()
    if registro is None:
        raise NotFound("Conteúdo não encontrado.")
    usuario = current_user()
    if not registro.homebrew and not usuario.is_admin:
        raise Forbidden("Apenas ADMIN remove conteúdo oficial.")
    db.session.delete(registro)
    db.session.commit()
    return ok({"removido": slug})
