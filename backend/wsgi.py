"""Ponto de entrada WSGI (gunicorn) e CLI de desenvolvimento."""
from app import create_app
from app.extensions import db

app = create_app()


@app.cli.command("init-db")
def init_db():
    """Cria as tabelas do banco."""
    db.create_all()
    print("Tabelas criadas.")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5050, debug=True)
