"""Endpoints de administração da plataforma (somente ADMIN)."""
from flask import Blueprint, request

from app.extensions import db
from app.models.campaign import MembroMesa, Mesa
from app.models.character import Personagem
from app.models.monster import Monstro
from app.models.user import PAPEIS_VALIDOS, User
from app.utils.auth import current_user, role_required
from app.utils.errors import NotFound, ValidationError
from app.utils.responses import corpo_json, ok

bp = Blueprint("admin", __name__)


@bp.get("/admin/users")
@role_required("ADMIN")
def listar_usuarios():
    """Lista usuários com filtros opcionais `q` (nome/email) e `role`."""
    consulta = User.query
    busca = request.args.get("q")
    papel = request.args.get("role")
    if busca:
        like = f"%{busca}%"
        consulta = consulta.filter((User.name.ilike(like)) | (User.email.ilike(like)))
    if papel:
        consulta = consulta.filter(User.role == papel.upper())
    usuarios = consulta.order_by(User.created_at.desc()).all()
    return ok([usuario.to_dict() for usuario in usuarios], meta={"total": len(usuarios)})


@bp.put("/admin/users/<int:user_id>/role")
@role_required("ADMIN")
def alterar_papel(user_id):
    """Promove/rebaixa o papel de um usuário."""
    dados = corpo_json(["role"])
    papel = (dados["role"] or "").upper()
    if papel not in PAPEIS_VALIDOS:
        raise ValidationError("Papel inválido.", details={"validos": list(PAPEIS_VALIDOS)})
    usuario = User.query.get(user_id)
    if usuario is None:
        raise NotFound("Usuário não encontrado.")
    usuario.role = papel
    db.session.commit()
    return ok(usuario.to_dict())


@bp.delete("/admin/users/<int:user_id>")
@role_required("ADMIN")
def remover_usuario(user_id):
    """Remove um usuário (ADMIN não pode deletar a si mesmo)."""
    if user_id == current_user().id:
        raise ValidationError("Você não pode remover a própria conta.")
    usuario = User.query.get(user_id)
    if usuario is None:
        raise NotFound("Usuário não encontrado.")
    db.session.delete(usuario)
    db.session.commit()
    return ok({"removido": user_id})


@bp.get("/admin/campaigns")
@role_required("ADMIN")
def listar_mesas():
    """Lista TODAS as mesas da plataforma (moderação)."""
    consulta = Mesa.query
    busca = request.args.get("q")
    if busca:
        consulta = consulta.filter(Mesa.nome.ilike(f"%{busca}%"))
    mesas = consulta.order_by(Mesa.created_at.desc()).all()
    return ok([mesa.to_dict() for mesa in mesas], meta={"total": len(mesas)})


@bp.delete("/admin/campaigns/<int:mesa_id>")
@role_required("ADMIN")
def remover_mesa(mesa_id):
    """Remove qualquer mesa ('desbugar')."""
    mesa = Mesa.query.get(mesa_id)
    if mesa is None:
        raise NotFound("Mesa não encontrada.")
    db.session.delete(mesa)
    db.session.commit()
    return ok({"removido": mesa_id})


@bp.post("/admin/campaigns/<int:mesa_id>/kick")
@role_required("ADMIN")
def expulsar_membro(mesa_id):
    """Tira um membro preso de qualquer mesa (suporte/moderação)."""
    mesa = Mesa.query.get(mesa_id)
    if mesa is None:
        raise NotFound("Mesa não encontrada.")
    dados = corpo_json(["user_id"])
    membro = MembroMesa.query.filter_by(mesa_id=mesa_id, user_id=int(dados["user_id"])).first()
    if membro is None:
        raise NotFound("Membro não encontrado na mesa.")
    for personagem in Personagem.query.filter_by(mesa_id=mesa_id, user_id=membro.user_id).all():
        personagem.mesa_id = None
    db.session.delete(membro)
    db.session.commit()
    return ok(mesa.to_dict(detalhado=True))


@bp.get("/admin/stats")
@role_required("ADMIN")
def estatisticas():
    """Métricas agregadas da plataforma."""
    por_papel = {
        papel: User.query.filter_by(role=papel).count()
        for papel in PAPEIS_VALIDOS
    }
    return ok({
        "usuarios": por_papel,
        "total_usuarios": User.query.count(),
        "personagens": Personagem.query.count(),
        "mesas": Mesa.query.count(),
        "monstros": Monstro.query.count(),
    })
