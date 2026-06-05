"""Endpoints de Mesas/Campanhas: mestre gerencia, jogadores entram por código."""
from flask import Blueprint

from app.extensions import db
from app.models.campaign import MembroMesa, Mesa
from app.models.character import Personagem
from app.utils.auth import auth_required, current_user, role_required
from app.utils.errors import Forbidden, NotFound, ValidationError
from app.utils.responses import corpo_json, created, ok

bp = Blueprint("campaigns", __name__)


def _mesa_ou_404(mesa_id):
    mesa = Mesa.query.get(mesa_id)
    if mesa is None:
        raise NotFound("Mesa não encontrada.")
    return mesa


@bp.get("/campaigns")
@auth_required
def listar():
    """Mesas onde o usuário é mestre OU membro."""
    usuario = current_user()
    mestradas = Mesa.query.filter_by(mestre_id=usuario.id).all()
    ids_participando = [
        membro.mesa_id
        for membro in MembroMesa.query.filter_by(user_id=usuario.id).all()
    ]
    participando = Mesa.query.filter(Mesa.id.in_(ids_participando)).all() if ids_participando else []

    vistas = {mesa.id: mesa for mesa in (mestradas + participando)}
    return ok(
        [mesa.to_dict() for mesa in vistas.values()],
        meta={"total": len(vistas)},
    )


@bp.post("/campaigns")
@role_required("MESTRE")
def criar():
    """Cria uma mesa (apenas MESTRE/ADMIN). Gera código de convite único."""
    dados = corpo_json(["nome"])
    mesa = Mesa(
        nome=dados["nome"],
        mestre_id=current_user().id,
        descricao=dados.get("descricao"),
    )
    # Garante unicidade do código.
    while Mesa.query.filter_by(codigo_convite=mesa.codigo_convite).first():
        mesa.codigo_convite = Mesa.gerar_codigo()
    db.session.add(mesa)
    db.session.commit()
    return created(mesa.to_dict(detalhado=True))


@bp.get("/campaigns/<int:mesa_id>")
@auth_required
def obter(mesa_id):
    """Detalhe da mesa (mestre, membro ou ADMIN)."""
    mesa = _mesa_ou_404(mesa_id)
    if not mesa.pode_ver(current_user()):
        raise Forbidden("Você não participa desta mesa.")
    return ok(mesa.to_dict(detalhado=True))


@bp.put("/campaigns/<int:mesa_id>")
@auth_required
def atualizar(mesa_id):
    """Atualiza a mesa (somente mestre/ADMIN)."""
    usuario = current_user()
    mesa = _mesa_ou_404(mesa_id)
    if not (usuario.is_admin or mesa.mestre_id == usuario.id):
        raise Forbidden("Apenas o mestre pode editar a mesa.")
    dados = corpo_json()
    if "nome" in dados:
        mesa.nome = dados["nome"]
    if "descricao" in dados:
        mesa.descricao = dados["descricao"]
    db.session.commit()
    return ok(mesa.to_dict(detalhado=True))


@bp.delete("/campaigns/<int:mesa_id>")
@auth_required
def remover(mesa_id):
    """Remove a mesa (somente mestre/ADMIN)."""
    usuario = current_user()
    mesa = _mesa_ou_404(mesa_id)
    if not (usuario.is_admin or mesa.mestre_id == usuario.id):
        raise Forbidden("Apenas o mestre pode remover a mesa.")
    db.session.delete(mesa)
    db.session.commit()
    return ok({"removido": mesa_id})


@bp.post("/campaigns/join")
@auth_required
def entrar():
    """Entra numa mesa informando o código de convite (idempotente)."""
    dados = corpo_json(["codigo"])
    codigo = (dados["codigo"] or "").strip().upper()
    mesa = Mesa.query.filter_by(codigo_convite=codigo).first()
    if mesa is None:
        raise NotFound("Código de convite inválido.")

    usuario = current_user()
    if mesa.mestre_id == usuario.id:
        raise ValidationError("Você já é o mestre desta mesa.")
    if not mesa.tem_membro(usuario.id):
        db.session.add(MembroMesa(mesa_id=mesa.id, user_id=usuario.id))
        db.session.commit()
    return ok(mesa.to_dict(detalhado=True))


@bp.post("/campaigns/<int:mesa_id>/kick")
@auth_required
def expulsar(mesa_id):
    """Remove um jogador da mesa (somente mestre/ADMIN)."""
    usuario = current_user()
    mesa = _mesa_ou_404(mesa_id)
    if not (usuario.is_admin or mesa.mestre_id == usuario.id):
        raise Forbidden("Apenas o mestre pode remover jogadores.")
    dados = corpo_json(["user_id"])
    membro = MembroMesa.query.filter_by(mesa_id=mesa.id, user_id=int(dados["user_id"])).first()
    if membro is None:
        raise NotFound("Jogador não está na mesa.")
    # Desvincula personagens daquele jogador na mesa.
    for personagem in Personagem.query.filter_by(mesa_id=mesa.id, user_id=membro.user_id).all():
        personagem.mesa_id = None
    db.session.delete(membro)
    db.session.commit()
    return ok(mesa.to_dict(detalhado=True))


@bp.post("/campaigns/<int:mesa_id>/personagens")
@auth_required
def vincular_personagem(mesa_id):
    """Vincula um personagem do usuário à mesa (precisa ser membro ou mestre)."""
    usuario = current_user()
    mesa = _mesa_ou_404(mesa_id)
    if not mesa.pode_ver(usuario):
        raise Forbidden("Você não participa desta mesa.")
    dados = corpo_json(["personagem_id"])
    personagem = Personagem.query.get(int(dados["personagem_id"]))
    if personagem is None or personagem.user_id != usuario.id:
        raise NotFound("Personagem não encontrado.")
    personagem.mesa_id = mesa.id
    db.session.commit()
    return ok(personagem.to_dict(incluir_derivados=False))
