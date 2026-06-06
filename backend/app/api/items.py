"""
CRUD de Armas, Armaduras e Itens com ownership.

Regras de ownership na criação:
- JOGADOR: o item é **vinculado ao seu personagem** (`personagem_id`) — só ele usa.
- MESTRE/ADMIN: vai para o **acervo geral** (global) ou para a mesa (`mesa_id`) do mestre.
Tudo criado na UI é `homebrew=True` com `fonte` obrigatória (nunca "oficial").
"""
from flask import Blueprint, request

from app.extensions import db
from app.models.character import Personagem
from app.models.items import Arma, Armadura, Item
from app.utils.auth import auth_required, current_user
from app.utils.errors import Forbidden, NotFound, ValidationError
from app.utils.responses import corpo_json, created, ok

bp = Blueprint("items", __name__)

# tipo de rota -> (Model, campos aceitos no corpo)
TIPOS = {
    "weapons": (Arma, ["slug", "nome", "descricao", "categoria", "alcance", "dano",
                       "tipo_dano", "propriedades", "bonus_magico", "efeitos"]),
    "armor": (Armadura, ["slug", "nome", "descricao", "categoria", "ca_base", "ca_soma_des",
                        "ca_des_max", "ca_bonus", "requisito_forca", "furtividade_desvantagem",
                        "bonus_magico", "efeitos"]),
    "items": (Item, ["slug", "nome", "descricao", "tipo_item", "raridade", "requer_sintonia"]),
}


def _modelo(tipo):
    if tipo not in TIPOS:
        raise NotFound("Tipo de item inválido.")
    return TIPOS[tipo]


def _meu_personagem(usuario, personagem_id):
    personagem = Personagem.query.get(int(personagem_id))
    if personagem is None or personagem.user_id != usuario.id:
        raise NotFound("Personagem não encontrado.")
    return personagem


@bp.get("/catalog/<tipo>")
@auth_required
def listar(tipo):
    """Catálogo global + (se ?personagem_id=) os itens próprios daquele personagem."""
    modelo, _campos = _modelo(tipo)
    usuario = current_user()
    consulta = modelo.query.filter(modelo.personagem_id.is_(None), modelo.mesa_id.is_(None))
    busca = request.args.get("q")
    if busca:
        consulta = consulta.filter(modelo.nome.ilike(f"%{busca}%"))
    globais = consulta.order_by(modelo.nome).limit(200).all()

    proprios = []
    pid = request.args.get("personagem_id")
    if pid:
        personagem = Personagem.query.get(int(pid))
        if personagem and (personagem.user_id == usuario.id or usuario.is_admin):
            proprios = modelo.query.filter_by(personagem_id=personagem.id).all()
    dados = [r.to_dict() for r in proprios + globais]

    if request.args.get("idioma") == "pt":
        from app.services.tradutor import Tradutor
        tradutor = Tradutor("pt")
        dados = [tradutor.aplicar(tipo, d) for d in dados]

    return ok(dados, meta={"total": len(proprios) + len(globais)})


@bp.get("/catalog/<tipo>/<int:item_id>")
@auth_required
def obter(tipo, item_id):
    modelo, _campos = _modelo(tipo)
    registro = modelo.query.get(item_id)
    if registro is None:
        raise NotFound("Item não encontrado.")
    return ok(registro.to_dict())


@bp.post("/catalog/<tipo>")
@auth_required
def criar(tipo):
    modelo, campos = _modelo(tipo)
    usuario = current_user()
    dados = corpo_json(["nome"])
    registro = modelo(nome=dados["nome"])
    for campo in campos:
        if campo in dados and campo != "nome":
            setattr(registro, campo, dados[campo])
    registro.criado_por = usuario.id
    registro.homebrew = True
    registro.fonte = dados.get("fonte") or f"Homebrew — {usuario.name}"

    if usuario.role == "JOGADOR":
        # Jogador: obrigatoriamente vinculado a um personagem seu.
        if not dados.get("personagem_id"):
            raise ValidationError("Informe o personagem ao qual o item pertence.")
        registro.personagem_id = _meu_personagem(usuario, dados["personagem_id"]).id
    else:
        # Mestre/Admin: acervo geral (ou da mesa, se mesa_id informado).
        if dados.get("mesa_id"):
            registro.mesa_id = int(dados["mesa_id"])

    db.session.add(registro)
    db.session.commit()
    return created(registro.to_dict())


@bp.put("/catalog/<tipo>/<int:item_id>")
@auth_required
def atualizar(tipo, item_id):
    modelo, campos = _modelo(tipo)
    registro = modelo.query.get(item_id)
    if registro is None:
        raise NotFound("Item não encontrado.")
    if not registro.pode_editar(current_user()):
        raise Forbidden("Você não pode editar este item.")
    dados = corpo_json()
    for campo in campos:
        if campo in dados:
            setattr(registro, campo, dados[campo])
    if "fonte" in dados and dados["fonte"]:
        registro.fonte = dados["fonte"]
    db.session.commit()
    return ok(registro.to_dict())


@bp.delete("/catalog/<tipo>/<int:item_id>")
@auth_required
def remover(tipo, item_id):
    modelo, _campos = _modelo(tipo)
    registro = modelo.query.get(item_id)
    if registro is None:
        raise NotFound("Item não encontrado.")
    if not registro.pode_editar(current_user()):
        raise Forbidden("Você não pode remover este item.")
    db.session.delete(registro)
    db.session.commit()
    return ok({"removido": item_id})
