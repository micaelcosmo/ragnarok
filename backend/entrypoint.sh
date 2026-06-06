#!/usr/bin/env bash
# Entrypoint: espera o Postgres, roda o seed (idempotente) e sobe o gunicorn.
set -e

echo "[entrypoint] aguardando o banco de dados..."
python - <<'PY'
import os, time
import sqlalchemy

url = os.getenv("DATABASE_URL", "postgresql+psycopg2://ragnarok:ragnarok@db:5432/ragnarok")
engine = sqlalchemy.create_engine(url)
for tentativa in range(30):
    try:
        with engine.connect() as conexao:
            conexao.execute(sqlalchemy.text("SELECT 1"))
        print("[entrypoint] banco disponível.")
        break
    except Exception as erro:
        print(f"[entrypoint] tentativa {tentativa + 1}/30: {erro}")
        time.sleep(2)
else:
    raise SystemExit("[entrypoint] banco não respondeu a tempo.")
PY

echo "[entrypoint] aplicando migrações (flask db upgrade)..."
export FLASK_APP=wsgi
flask db upgrade || echo "[entrypoint] aviso: upgrade falhou (banco já no head?), seguindo."

echo "[entrypoint] populando o banco (seed idempotente)..."
python -m app.seed || echo "[entrypoint] aviso: seed falhou, seguindo mesmo assim."

echo "[entrypoint] iniciando gunicorn na porta 5050..."
exec gunicorn --bind 0.0.0.0:5050 --workers 3 --timeout 60 wsgi:app
