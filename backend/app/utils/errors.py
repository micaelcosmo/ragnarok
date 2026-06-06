"""Erros de API padronizados em JSON: {"error": {"code","message","details"}}."""
from flask import jsonify


class ApiError(Exception):
    status_code = 400
    code = "VALIDATION"

    def __init__(self, message, code=None, status_code=None, details=None):
        super().__init__(message)
        self.message = message
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code
        self.details = details or {}

    def to_response(self):
        payload = {"error": {"code": self.code, "message": self.message}}
        if self.details:
            payload["error"]["details"] = self.details
        return jsonify(payload), self.status_code


class ValidationError(ApiError):
    status_code = 400
    code = "VALIDATION"


class Unauthorized(ApiError):
    status_code = 401
    code = "UNAUTHORIZED"


class Forbidden(ApiError):
    status_code = 403
    code = "FORBIDDEN"


class NotFound(ApiError):
    status_code = 404
    code = "NOT_FOUND"


class Conflict(ApiError):
    status_code = 409
    code = "CONFLICT"


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def _handle_api_error(err: ApiError):
        return err.to_response()

    @app.errorhandler(404)
    def _handle_404(_err):
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Recurso não encontrado."}}), 404

    @app.errorhandler(405)
    def _handle_405(_err):
        return jsonify({"error": {"code": "METHOD_NOT_ALLOWED", "message": "Método não permitido."}}), 405

    @app.errorhandler(500)
    def _handle_500(err):
        app.logger.exception("Erro interno: %s", err)
        return jsonify({"error": {"code": "INTERNAL", "message": "Erro interno do servidor."}}), 500
