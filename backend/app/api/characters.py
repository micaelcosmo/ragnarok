"""Endpoints de Personagens (ficha 5E). Ownership por jogador; mestre vê os da sua mesa."""
from flask import Blueprint, request

from app.extensions import db
from app.models.campaign import Mesa
from app.models.character import Personagem
from app.utils.auth import auth_required, current_user
from app.utils.errors import Forbidden, NotFound
from app.utils.responses import corpo_json, created, ok

bp = Blueprint("characters", __name__)

# Mapa atributo curto -> coluna do model.
_ATRIBUTOS = Personagem.ATRIBUTOS_COLUNAS

# Campos simples atualizáveis diretamente do corpo.
_CAMPOS_TEXTO = (
    "nome", "nome_jogador", "raca_slug", "classe_slug", "antecedente_slug",
    "tendencia", "deslocamento", "dado_vida", "outras_proficiencias",
    "classe_conjuradora", "atributo_conjuracao", "tracos_personalidade",
    "ideais", "vinculos", "fraquezas", "historia", "caracteristicas",
    "idiomas", "equipamento", "ataques", "dinheiro", "avatar_url",
)
_CAMPOS_INT = (
    "nivel", "xp", "ca", "ca_ajuste", "iniciativa_bonus", "pv_max", "pv_atual", "pv_temp",
)
_CAMPOS_LISTA = (
    "pericias_proficientes", "salvaguardas_proficientes", "truques", "magias", "talentos",
)


def _personagem_acessivel(personagem, usuario):
    """Dono, ADMIN ou mestre da mesa do personagem podem acessar."""
    if usuario.is_admin or personagem.user_id == usuario.id:
        return True
    if personagem.mesa_id is not None:
        mesa = Mesa.query.get(personagem.mesa_id)
        if mesa is not None and mesa.mestre_id == usuario.id:
            return True
    return False


def _aplicar_campos(personagem, dados):
    """Aplica os campos enviados ao personagem (POO: encapsula a atribuição)."""
    for campo in _CAMPOS_TEXTO:
        if campo in dados:
            setattr(personagem, campo, dados[campo])
    for campo in _CAMPOS_INT:
        if campo in dados and dados[campo] is not None:
            try:
                setattr(personagem, campo, int(dados[campo]))
            except (TypeError, ValueError):
                pass
    for campo in _CAMPOS_LISTA:
        if campo in dados and isinstance(dados[campo], list):
            setattr(personagem, campo, dados[campo])
    if "inspiracao" in dados:
        personagem.inspiracao = bool(dados["inspiracao"])

    atributos = dados.get("atributos")
    if isinstance(atributos, dict):
        for chave, coluna in _ATRIBUTOS.items():
            if chave in atributos and atributos[chave] is not None:
                try:
                    setattr(personagem, coluna, int(atributos[chave]))
                except (TypeError, ValueError):
                    pass


@bp.get("/characters")
@auth_required
def listar():
    """Lista personagens do usuário; mestre pode filtrar por `?mesa_id=`."""
    usuario = current_user()
    mesa_id = request.args.get("mesa_id")

    if mesa_id:
        mesa = Mesa.query.get(int(mesa_id))
        if mesa is None:
            raise NotFound("Mesa não encontrada.")
        if not (usuario.is_admin or mesa.mestre_id == usuario.id or mesa.tem_membro(usuario.id)):
            raise Forbidden("Você não participa desta mesa.")
        personagens = Personagem.query.filter_by(mesa_id=mesa.id).all()
    else:
        personagens = Personagem.query.filter_by(user_id=usuario.id).all()

    return ok(
        [personagem.to_dict(incluir_derivados=False) for personagem in personagens],
        meta={"total": len(personagens)},
    )


@bp.post("/characters")
@auth_required
def criar():
    """Cria um personagem para o usuário atual."""
    dados = corpo_json(["nome"])
    personagem = Personagem(user_id=current_user().id, nome=dados["nome"])
    _aplicar_campos(personagem, dados)
    # PV inicial coerente se não enviado.
    if personagem.pv_atual in (None, 0):
        personagem.pv_atual = personagem.pv_max
    db.session.add(personagem)
    db.session.commit()
    return created(personagem.to_dict())


@bp.get("/characters/<int:personagem_id>")
@auth_required
def obter(personagem_id):
    """Retorna a ficha completa com campos derivados."""
    personagem = Personagem.query.get(personagem_id)
    if personagem is None:
        raise NotFound("Personagem não encontrado.")
    if not _personagem_acessivel(personagem, current_user()):
        raise Forbidden("Você não pode ver este personagem.")
    return ok(personagem.to_dict())


@bp.put("/characters/<int:personagem_id>")
@auth_required
def atualizar(personagem_id):
    """Atualiza a ficha (somente dono ou ADMIN)."""
    usuario = current_user()
    personagem = Personagem.query.get(personagem_id)
    if personagem is None:
        raise NotFound("Personagem não encontrado.")
    if not (usuario.is_admin or personagem.user_id == usuario.id):
        raise Forbidden("Você não pode editar este personagem.")
    dados = corpo_json()
    _aplicar_campos(personagem, dados)
    db.session.commit()
    return ok(personagem.to_dict())


@bp.delete("/characters/<int:personagem_id>")
@auth_required
def remover(personagem_id):
    """Remove a ficha (somente dono ou ADMIN)."""
    usuario = current_user()
    personagem = Personagem.query.get(personagem_id)
    if personagem is None:
        raise NotFound("Personagem não encontrado.")
    if not (usuario.is_admin or personagem.user_id == usuario.id):
        raise Forbidden("Você não pode remover este personagem.")
    db.session.delete(personagem)
    db.session.commit()
    return ok({"removido": personagem_id})
