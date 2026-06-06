"""Fixtures de teste: app em memória, client e fábrica de usuários autenticados."""
import pytest
from flask_jwt_extended import create_access_token

from app import create_app
from app.extensions import db as _db
from app.models.user import User


@pytest.fixture()
def app():
    aplicacao = create_app("test")
    with aplicacao.app_context():
        _db.create_all()
        yield aplicacao
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    return _db


@pytest.fixture()
def make_user(app):
    """Cria um usuário com papel dado e retorna (user, token)."""
    contador = {"n": 0}

    def _criar(role="JOGADOR", email=None, password="senha123", name=None):
        contador["n"] += 1
        email = email or f"user{contador['n']}@teste.local"
        name = name or f"Usuário {contador['n']}"
        usuario = User(email=email, name=name, password=password, role=role)
        _db.session.add(usuario)
        _db.session.commit()
        token = create_access_token(identity=str(usuario.id))
        return usuario, token

    return _criar


@pytest.fixture()
def auth():
    """Monta o header Authorization a partir de um token."""
    def _header(token):
        return {"Authorization": f"Bearer {token}"}

    return _header
