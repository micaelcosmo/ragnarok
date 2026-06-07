# Backend Ragnarok — API Flask servida por gunicorn.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependências de sistema: psycopg2 (gcc/libpq) + WeasyPrint (pango/cairo/gdk-pixbuf) p/ export PDF.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc libpq-dev curl \
        libpango-1.0-0 libpangocairo-1.0-0 libcairo2 libgdk-pixbuf-2.0-0 \
        libffi-dev shared-mime-info fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh

EXPOSE 5050

ENTRYPOINT ["./entrypoint.sh"]
