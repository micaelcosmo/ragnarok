"""App factory do Ragnarok."""
from flask import Flask, jsonify

from app.config import get_config
from app.extensions import cors, db, jwt, migrate
from app.utils.errors import register_error_handlers


def create_app(config_name=None):
    """Cria e configura a aplicação Flask (padrão app factory)."""
    app = Flask(__name__)
    config = get_config(config_name)
    config.validate()  # fail-fast: aborta em prod se faltar segredo obrigatório
    app.config.from_object(config)

    _registrar_extensoes(app)
    _registrar_jwt_handlers(app)
    register_error_handlers(app)
    _registrar_blueprints(app)

    return app


def _registrar_extensoes(app):
    db.init_app(app)
    # Importa os models para que o Alembic enxergue todas as tabelas no autogenerate.
    # (usa 'from ... import' para NÃO rebind/sombrear o parâmetro `app`).
    from app import models as _models  # noqa: F401
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})


def _registrar_jwt_handlers(app):
    @jwt.unauthorized_loader
    def _sem_token(motivo):
        return jsonify({"error": {"code": "UNAUTHORIZED", "message": "Token ausente."}}), 401

    @jwt.invalid_token_loader
    def _token_invalido(motivo):
        return jsonify({"error": {"code": "UNAUTHORIZED", "message": "Token inválido."}}), 401

    @jwt.expired_token_loader
    def _token_expirado(cabecalho, payload):
        return jsonify({"error": {"code": "UNAUTHORIZED", "message": "Token expirado."}}), 401


def _registrar_blueprints(app):
    from app.api.health import bp as health_bp
    from app.api.auth import bp as auth_bp
    from app.api.reference import bp as reference_bp
    from app.api.characters import bp as characters_bp
    from app.api.campaigns import bp as campaigns_bp
    from app.api.bestiary import bp as bestiary_bp
    from app.api.admin import bp as admin_bp

    for blueprint in (
        health_bp,
        auth_bp,
        reference_bp,
        characters_bp,
        campaigns_bp,
        bestiary_bp,
        admin_bp,
    ):
        app.register_blueprint(blueprint, url_prefix="/api/v1")
