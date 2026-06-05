"""Endpoints do Bestiário (monstros e PDMs). SRD global + bestiário por mesa."""
from flask import Blueprint, request
from sqlalchemy import or_

from app.extensions import db
from app.models.campaign import Mesa
from app.models.monster import Monstro
from app.utils.auth import auth_required, current_user, role_required
from app.utils.errors import Forbidden, NotFound
from app.utils.responses import corpo_json, created, ok

bp = Blueprint("bestiary", __name__)

_CAMPOS = (
    "slug", "nome", "tipo", "tamanho", "alinhamento", "ca", "pv", "pv_formula",
    "deslocamento", "atributos", "nd", "xp", "pericias", "sentidos", "idiomas",
    "habilidades", "acoes", "is_pdm",
)


def _aplicar_campos(monstro, dados):
    for campo in _CAMPOS:
        if campo in dados:
            setattr(monstro, campo, dados[campo])


@bp.get("/bestiary")
@auth_required
def listar():
    """SRD global (mesa_id nulo) + (se `?mesa_id=`) bestiário da mesa."""
    usuario = current_user()
    consulta = Monstro.query
    mesa_id = request.args.get("mesa_id")
    busca = request.args.get("q")

    if mesa_id:
        mesa = Mesa.query.get(int(mesa_id))
        if mesa is None:
            raise NotFound("Mesa não encontrada.")
        if not mesa.pode_ver(usuario):
            raise Forbidden("Você não participa desta mesa.")
        consulta = consulta.filter(
            or_(Monstro.mesa_id.is_(None), Monstro.mesa_id == mesa.id)
        )
    else:
        consulta = consulta.filter(Monstro.mesa_id.is_(None))

    if busca:
        consulta = consulta.filter(Monstro.nome.ilike(f"%{busca}%"))

    monstros = consulta.order_by(Monstro.nome).all()
    return ok([monstro.to_dict() for monstro in monstros], meta={"total": len(monstros)})


@bp.get("/bestiary/<int:monstro_id>")
@auth_required
def obter(monstro_id):
    monstro = Monstro.query.get(monstro_id)
    if monstro is None:
        raise NotFound("Criatura não encontrada.")
    return ok(monstro.to_dict())


@bp.post("/bestiary")
@role_required("MESTRE")
def criar():
    """Cria monstro/PDM. Com `mesa_id` cria na mesa (só mestre dela); sem ela + ADMIN = SRD global."""
    usuario = current_user()
    dados = corpo_json(["nome"])
    mesa_id = dados.get("mesa_id")

    if mesa_id:
        mesa = Mesa.query.get(int(mesa_id))
        if mesa is None:
            raise NotFound("Mesa não encontrada.")
        if not (usuario.is_admin or mesa.mestre_id == usuario.id):
            raise Forbidden("Apenas o mestre da mesa pode adicionar criaturas a ela.")
    elif not usuario.is_admin:
        raise Forbidden("Apenas ADMIN cria conteúdo SRD global.")

    monstro = Monstro(nome=dados["nome"], mesa_id=mesa_id, criado_por=usuario.id)
    _aplicar_campos(monstro, dados)
    db.session.add(monstro)
    db.session.commit()
    return created(monstro.to_dict())


@bp.put("/bestiary/<int:monstro_id>")
@auth_required
def atualizar(monstro_id):
    monstro = Monstro.query.get(monstro_id)
    if monstro is None:
        raise NotFound("Criatura não encontrada.")
    mesa = Mesa.query.get(monstro.mesa_id) if monstro.mesa_id else None
    if not monstro.pode_editar(current_user(), mesa):
        raise Forbidden("Você não pode editar esta criatura.")
    _aplicar_campos(monstro, corpo_json())
    db.session.commit()
    return ok(monstro.to_dict())


@bp.delete("/bestiary/<int:monstro_id>")
@auth_required
def remover(monstro_id):
    monstro = Monstro.query.get(monstro_id)
    if monstro is None:
        raise NotFound("Criatura não encontrada.")
    mesa = Mesa.query.get(monstro.mesa_id) if monstro.mesa_id else None
    if not monstro.pode_editar(current_user(), mesa):
        raise Forbidden("Você não pode remover esta criatura.")
    db.session.delete(monstro)
    db.session.commit()
    return ok({"removido": monstro_id})
