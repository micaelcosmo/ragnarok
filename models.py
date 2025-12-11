from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


# Inicializamos o objeto db sem o 'app' aqui para evitar importação circular.
db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    # Relacionamento opcional: Se cada ficha pertencer a um usuário
    # fichas = db.relationship('Ficha', backref='dono', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
# ==============================================================================
# MODELOS DE BANCO DE DADOS
# ==============================================================================

class Modelo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    
    # Cascata: Deletar Modelo -> Deleta Campos e Fichas
    campos = db.relationship('Campo', backref='modelo', cascade="all, delete-orphan")
    personagens = db.relationship('Personagem', backref='modelo', cascade="all, delete-orphan")

class Campo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    modelo_id = db.Column(db.Integer, db.ForeignKey('modelo.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    
    # Cascata: Deletar Campo -> Deleta Valores
    valores = db.relationship('Valor', backref='campo', cascade="all, delete-orphan")

class Personagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    modelo_id = db.Column(db.Integer, db.ForeignKey('modelo.id'), nullable=False)
    
    # --- CABEÇALHO PADRÃO (Colunas Fixas) ---
    nome = db.Column(db.String(100), nullable=False)          # Nome do Personagem
    raca = db.Column(db.String(50), nullable=True)            # Raça
    classe = db.Column(db.String(50), nullable=True)          # Classe
    nivel = db.Column(db.Integer, default=1)                  # Nível
    nome_jogador = db.Column(db.String(100), nullable=True)   # Nome do Jogador
    
    # Cascata: Deletar Personagem -> Deleta seus Valores
    valores = db.relationship('Valor', backref='personagem', cascade="all, delete-orphan")

class Valor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    personagem_id = db.Column(db.Integer, db.ForeignKey('personagem.id'), nullable=False)
    campo_id = db.Column(db.Integer, db.ForeignKey('campo.id'), nullable=False)
    valor_texto = db.Column(db.String(500), nullable=True)