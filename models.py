from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    personagens = db.relationship('Personagem', backref='dono', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Modelo(db.Model):
    __tablename__ = 'modelos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255), nullable=True)
    
    campos = db.relationship('Campo', backref='modelo', cascade="all, delete-orphan", order_by="Campo.ordem")
    personagens = db.relationship('Personagem', backref='modelo_base', cascade="all, delete-orphan")


class Campo(db.Model):
    __tablename__ = 'campos'

    id = db.Column(db.Integer, primary_key=True)
    modelo_id = db.Column(db.Integer, db.ForeignKey('modelos.id'), nullable=False)
    
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False) 
    categoria = db.Column(db.String(100), nullable=False, default='Geral')
    ordem = db.Column(db.Integer, default=0)
    
    valores = db.relationship('Valor', backref='campo_referencia', cascade="all, delete-orphan")


class Personagem(db.Model):
    __tablename__ = 'personagens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    modelo_id = db.Column(db.Integer, db.ForeignKey('modelos.id'), nullable=False)
    
    nome = db.Column(db.String(100), nullable=False)
    raca = db.Column(db.String(50), nullable=True)
    classe = db.Column(db.String(50), nullable=True)
    nivel = db.Column(db.Integer, default=1)
    nome_jogador = db.Column(db.String(100), nullable=True)
    antecedente = db.Column(db.String(100), nullable=True)
    tendencia = db.Column(db.String(50), nullable=True)
    xp = db.Column(db.Integer, default=0)
    
    valores = db.relationship('Valor', backref='personagem_dono', cascade="all, delete-orphan")


class Valor(db.Model):
    __tablename__ = 'valores'

    id = db.Column(db.Integer, primary_key=True)
    personagem_id = db.Column(db.Integer, db.ForeignKey('personagens.id'), nullable=False)
    campo_id = db.Column(db.Integer, db.ForeignKey('campos.id'), nullable=False)
    valor_texto = db.Column(db.Text, nullable=True)