"""
Upload de imagens (retrato do personagem, símbolo da facção).

Segurança:
- allowlist de extensão (png/jpg/jpeg/webp);
- **sniff de magic-bytes** (não confia na extensão nem no content-type do cliente);
- nome de arquivo gerado no servidor (uuid) — sem usar o caminho do cliente (anti path-traversal);
- limite de tamanho (Flask MAX_CONTENT_LENGTH + checagem do tamanho lido);
- servido como estático (sem execução).
"""
import os
import uuid

from flask import Blueprint, current_app, request, send_from_directory

from app.utils.auth import auth_required
from app.utils.errors import ValidationError
from app.utils.responses import ok

bp = Blueprint("uploads", __name__)

# extensão canônica -> assinaturas (magic bytes) aceitas
_ASSINATURAS = {
    "png": [b"\x89PNG\r\n\x1a\n"],
    "jpg": [b"\xff\xd8\xff"],
    "webp": [b"RIFF"],  # + 'WEBP' no offset 8 (checado abaixo)
}
_EXT_ALIAS = {"jpeg": "jpg"}
_MAX_BYTES = 2 * 1024 * 1024  # 2 MB


def _tipo_valido(dados: bytes, ext: str):
    """Confere a assinatura real do conteúdo contra a extensão declarada."""
    if ext == "webp":
        return dados[:4] == b"RIFF" and dados[8:12] == b"WEBP"
    return any(dados.startswith(assinatura) for assinatura in _ASSINATURAS.get(ext, []))


@bp.post("/uploads")
@auth_required
def enviar():
    """Recebe uma imagem (campo 'arquivo') e devolve a URL servível."""
    arquivo = request.files.get("arquivo")
    if arquivo is None or not arquivo.filename:
        raise ValidationError("Envie um arquivo no campo 'arquivo'.")

    ext = arquivo.filename.rsplit(".", 1)[-1].lower() if "." in arquivo.filename else ""
    ext = _EXT_ALIAS.get(ext, ext)
    if ext not in _ASSINATURAS:
        raise ValidationError("Tipo não permitido. Use png, jpg, jpeg ou webp.")

    dados = arquivo.read()
    if len(dados) == 0:
        raise ValidationError("Arquivo vazio.")
    if len(dados) > _MAX_BYTES:
        raise ValidationError("Imagem muito grande (máx. 2 MB).", status_code=413)
    if not _tipo_valido(dados, ext):
        raise ValidationError("O conteúdo do arquivo não é uma imagem válida.")

    pasta = current_app.config["UPLOAD_DIR"]
    os.makedirs(pasta, exist_ok=True)
    nome = f"{uuid.uuid4().hex}.{ext}"   # nome gerado no servidor (anti path-traversal)
    with open(os.path.join(pasta, nome), "wb") as destino:
        destino.write(dados)

    return ok({"url": f"/api/v1/uploads/{nome}", "nome": nome})


@bp.get("/uploads/<nome>")
def servir(nome):
    """Serve o arquivo (fallback; em produção o nginx serve direto do volume)."""
    # Só nomes no formato gerado (hex + extensão permitida) — bloqueia traversal.
    if "/" in nome or "\\" in nome or ".." in nome:
        raise ValidationError("Nome inválido.")
    ext = nome.rsplit(".", 1)[-1].lower() if "." in nome else ""
    if ext not in _ASSINATURAS:
        raise ValidationError("Tipo inválido.")
    return send_from_directory(current_app.config["UPLOAD_DIR"], nome)
