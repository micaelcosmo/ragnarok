"""
CLI da pipeline de conteúdo.

Exemplos:
    python -m app.content.cli --source local
    python -m app.content.cli --source open5e --types feats,races,spells
    python -m app.content.cli --source open5e --types monsters --limit 100 --force
"""
import argparse

from app import create_app
from app.extensions import db
from app.content.base import TIPOS
from app.content.local_source import LocalSource
from app.content.open5e_source import Open5eSource
from app.content.pipeline import ContentPipeline


def _criar_source(nome, limite):
    if nome == "local":
        return LocalSource()
    if nome == "open5e":
        return Open5eSource(limite=limite)
    raise SystemExit(f"Fonte desconhecida: {nome} (use 'local' ou 'open5e')")


def main():
    parser = argparse.ArgumentParser(description="Pipeline de conteúdo do Ragnarok")
    parser.add_argument("--source", default="local", help="local | open5e")
    parser.add_argument("--types", default=",".join(TIPOS),
                        help="lista separada por vírgula (ex.: feats,races,spells)")
    parser.add_argument("--limit", type=int, default=None, help="máximo de itens por tipo")
    parser.add_argument("--force", action="store_true", help="sobrescreve campos já preenchidos")
    args = parser.parse_args()

    tipos = [parte.strip() for parte in args.types.split(",") if parte.strip()]
    source = _criar_source(args.source, args.limit)

    app = create_app()
    with app.app_context():
        db.create_all()
        pipeline = ContentPipeline(source, force=args.force)
        relatorio = pipeline.executar(tipos)
    print(relatorio)


if __name__ == "__main__":
    main()
