"""Endpoints de administração da plataforma (somente ADMIN)."""
from flask import Blueprint, request

from app.extensions import db
from app.models.campaign import Mesa
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
