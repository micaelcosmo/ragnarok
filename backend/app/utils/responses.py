"""Helpers de resposta JSON no padrão da API."""
from flask import jsonify, request

from app.utils.errors import ValidationError


def ok(data, status=200, meta=None):
    """Resposta de sucesso no formato {"data": ...}."""
    payload = {"data": data}
    if meta is not None:
        payload["meta"] = meta
    return jsonify(payload), status


def created(data):
    """Resposta 201 para criação de recurso."""
    return ok(data, status=201)


def corpo_json(obrigatorios=None):
    """
    Lê e valida o corpo JSON da requisição. Garante que os campos `obrigatorios`
    estão presentes e não vazios; senão levanta ValidationError.
    """
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        raise ValidationError("Corpo JSON inválido ou ausente.")

    faltando = [
        campo
        for campo in (obrigatorios or [])
        if dados.get(campo) in (None, "")
    ]
    if faltando:
        raise ValidationError(
            "Campos obrigatórios ausentes.",
            details={campo: "obrigatório" for campo in faltando},
        )
    return dados
