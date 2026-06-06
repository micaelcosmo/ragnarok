"""Endpoints de autenticação: registro, login e perfil atual."""
import hashlib
import re

from flask import Blueprint
from flask_jwt_extended import create_access_token, decode_token

from app.extensions import db
from app.models.user import PAPEIS_VALIDOS, User
from app.utils.auth import auth_required, current_user
from app.utils.errors import Conflict, NotFound, Unauthorized, ValidationError
from app.utils.responses import corpo_json, created, ok

bp = Blueprint("auth", __name__)

SENHA_MINIMA = 6
# Validação pragmática de email (aceita domínios de estudo como .local).
_PADRAO_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validar_email(email):
    email = (email or "").strip().lower()
    if not _PADRAO_EMAIL.match(email):
        raise ValidationError("Email inválido.")
    return email


@bp.post("/auth/register")
def register():
    """Registra um novo usuário. ADMIN nunca é auto-atribuível."""
    dados = corpo_json(["email", "name", "password"])
    email = _validar_email(dados["email"])

    if len(dados["password"]) < SENHA_MINIMA:
        raise ValidationError(
            f"A senha deve ter ao menos {SENHA_MINIMA} caracteres."
        )

    if User.query.filter_by(email=email).first():
        raise Conflict("Email já cadastrado.")

    papel_pedido = (dados.get("role") or "JOGADOR").upper()
    # Segurança: ninguém se registra como ADMIN.
    if papel_pedido not in PAPEIS_VALIDOS or papel_pedido == "ADMIN":
        papel_pedido = "JOGADOR"

    usuario = User(
        email=email,
        name=dados["name"],
        password=dados["password"],
        role=papel_pedido,
    )
    db.session.add(usuario)
    db.session.commit()

    # Auto-login: devolve o token já no registro (evita o passo manual de re-login,
    # onde autofill do navegador ou erro de digitação causavam "credenciais inválidas").
    token = create_access_token(identity=str(usuario.id))
    return created({"access_token": token, "user": usuario.to_dict()})


@bp.post("/auth/login")
def login():
    """Autentica e devolve um access token JWT + dados do usuário."""
    dados = corpo_json(["email", "password"])
    email = (dados["email"] or "").strip().lower()
    usuario = User.query.filter_by(email=email).first()

    if usuario is None or not usuario.check_password(dados["password"]):
        raise Unauthorized("Credenciais inválidas.")

    token = create_access_token(identity=str(usuario.id))
    return ok({"access_token": token, "user": usuario.to_dict()})


@bp.get("/auth/me")
@auth_required
def me():
    """Retorna o usuário autenticado."""
    return ok(current_user().to_dict())


def _impressao_senha(usuario):
    """Fragmento do hash atual — invalida o link de reset assim que a senha muda."""
    return hashlib.sha256(usuario.password_hash.encode()).hexdigest()[:16]


@bp.post("/auth/reset-password")
def reset_password():
    """
    Redefine a senha usando um token de redefinição (gerado pelo admin).
    Não exige a senha antiga — só o token válido + a nova senha.
    """
    dados = corpo_json(["token", "nova_senha"])
    if len(dados["nova_senha"]) < SENHA_MINIMA:
        raise ValidationError(f"A senha deve ter ao menos {SENHA_MINIMA} caracteres.")

    try:
        conteudo = decode_token(dados["token"])
    except Exception:
        raise Unauthorized("Link inválido ou expirado.")

    if conteudo.get("purpose") != "pwd_reset":
        raise Unauthorized("Token não é de redefinição de senha.")

    usuario = User.query.get(int(conteudo.get("sub")))
    if usuario is None:
        raise NotFound("Usuário não encontrado.")
    # O link deixa de valer quando a senha é trocada (uso único na prática).
    if conteudo.get("ph") != _impressao_senha(usuario):
        raise Unauthorized("Este link já foi usado ou expirou.")

    usuario.set_password(dados["nova_senha"])
    db.session.commit()

    # Auto-login após redefinir.
    token = create_access_token(identity=str(usuario.id))
    return ok({"access_token": token, "user": usuario.to_dict()})
