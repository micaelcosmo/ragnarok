from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configuração do SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'ragnarok.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- NOVOS MODELOS DE BANCO DE DADOS ---

class Modelo(db.Model):
    """Define um template de ficha (ex: D&D, Tormenta, Call of Cthulhu)"""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    campos = db.relationship('Campo', backref='modelo', cascade="all, delete-orphan")
    personagens = db.relationship('Personagem', backref='modelo', lazy=True)

class Campo(db.Model):
    """Define os campos disponíveis em um modelo"""
    id = db.Column(db.Integer, primary_key=True)
    modelo_id = db.Column(db.Integer, db.ForeignKey('modelo.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False) # 'texto', 'inteiro', 'booleano'

class Personagem(db.Model):
    """O personagem em si, vinculado a um modelo"""
    id = db.Column(db.Integer, primary_key=True)
    modelo_id = db.Column(db.Integer, db.ForeignKey('modelo.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    nivel = db.Column(db.Integer, default=1) # Mantive nível como padrão universal
    valores = db.relationship('Valor', backref='personagem', cascade="all, delete-orphan")

class Valor(db.Model):
    """O valor preenchido para um campo específico"""
    id = db.Column(db.Integer, primary_key=True)
    personagem_id = db.Column(db.Integer, db.ForeignKey('personagem.id'), nullable=False)
    campo_id = db.Column(db.Integer, db.ForeignKey('campo.id'), nullable=False)
    valor_texto = db.Column(db.String(500), nullable=True) # Armazenamos tudo como string e convertemos na view

    @property
    def valor_real(self):
        # Helper para retornar o tipo correto se necessário
        return self.valor_texto

# Cria o banco se não existir
with app.app_context():
    db.create_all()
    # Cria um modelo padrão se não houver nenhum
    if not Modelo.query.first():
        m = Modelo(nome="Aventureiro Padrão")
        db.session.add(m)
        db.session.flush()
        db.session.add(Campo(modelo_id=m.id, nome="Classe", tipo="texto"))
        db.session.add(Campo(modelo_id=m.id, nome="Raça", tipo="texto"))
        db.session.add(Campo(modelo_id=m.id, nome="Força", tipo="inteiro"))
        db.session.add(Campo(modelo_id=m.id, nome="Vivo?", tipo="booleano"))
        db.session.add(Campo(modelo_id=m.id, nome="História", tipo="texto"))
        db.session.commit()

# --- ROTAS ---

@app.route('/')
def index():
    personagens = Personagem.query.with_entities(Personagem.id, Personagem.nome).all()
    return render_template('index.html', personagens=personagens)

# --- GERENCIAMENTO DE MODELOS ---
@app.route('/modelos', methods=['GET', 'POST'])
def gerenciar_modelos():
    if request.method == 'POST':
        if 'novo_modelo' in request.form:
            novo = Modelo(nome=request.form['nome_modelo'])
            db.session.add(novo)
            db.session.commit()
        elif 'novo_campo' in request.form:
            modelo_id = request.form['modelo_id']
            campo = Campo(
                modelo_id=modelo_id,
                nome=request.form['nome_campo'],
                tipo=request.form['tipo_campo']
            )
            db.session.add(campo)
            db.session.commit()
        elif 'deletar_campo' in request.form:
            Campo.query.filter_by(id=request.form['campo_id']).delete()
            db.session.commit()
            
    modelos = Modelo.query.all()
    return render_template('modelos.html', modelos=modelos)

# --- PERSONAGENS ---

@app.route('/novo', methods=['GET', 'POST'])
def novo_personagem():
    # Passo 1: Selecionar Modelo
    if request.method == 'GET' and not request.args.get('modelo_id'):
        modelos = Modelo.query.all()
        return render_template('selecionar_modelo.html', modelos=modelos)

    # Passo 2: Preencher Ficha
    modelo_id = request.args.get('modelo_id') or request.form.get('modelo_id')
    modelo = Modelo.query.get_or_404(modelo_id)

    if request.method == 'POST' and 'salvar_ficha' in request.form:
        # Criar Personagem
        p = Personagem(
            nome=request.form['nome'],
            nivel=request.form['nivel'],
            modelo_id=modelo.id
        )
        db.session.add(p)
        db.session.flush() # Pega o ID do p

        # Salvar Valores Dinâmicos
        for campo in modelo.campos:
            chave_form = f'campo_{campo.id}'
            valor_bruto = request.form.get(chave_form)
            
            if campo.tipo == 'booleano':
                valor_bruto = 'Sim' if valor_bruto == 'on' else 'Não'
            
            v = Valor(personagem_id=p.id, campo_id=campo.id, valor_texto=valor_bruto)
            db.session.add(v)
        
        db.session.commit()
        return render_template('refresh_parent.html', id=p.id)
    
    return render_template('form.html', p=None, modelo=modelo)

@app.route('/ficha/<int:id>')
def ver_ficha(id):
    p = Personagem.query.get_or_404(id)
    # Dicionário para facilitar acesso no template: { 'Força': '18', 'Classe': 'Ranger' }
    valores_map = {v.campo_id: v.valor_texto for v in p.valores}
    return render_template('ficha.html', p=p, valores=valores_map)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_personagem(id):
    p = Personagem.query.get_or_404(id)
    modelo = p.modelo

    if request.method == 'POST':
        p.nome = request.form['nome']
        p.nivel = request.form['nivel']
        
        # Atualizar valores
        for campo in modelo.campos:
            chave_form = f'campo_{campo.id}'
            valor_bruto = request.form.get(chave_form)

            if campo.tipo == 'booleano':
                valor_bruto = 'Sim' if valor_bruto == 'on' else 'Não'
            
            # Procura valor existente ou cria novo
            v = Valor.query.filter_by(personagem_id=p.id, campo_id=campo.id).first()
            if v:
                v.valor_texto = valor_bruto
            else:
                v = Valor(personagem_id=p.id, campo_id=campo.id, valor_texto=valor_bruto)
                db.session.add(v)

        db.session.commit()
        return render_template('refresh_parent.html', id=p.id)

    # Mapeia valores existentes para pré-preencher form
    valores_map = {v.campo_id: v.valor_texto for v in p.valores}
    return render_template('form.html', p=p, modelo=modelo, valores=valores_map)

@app.route('/deletar/<int:id>')
def deletar_personagem(id):
    p = Personagem.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return render_template('refresh_parent.html', deleted=True)

if __name__ == '__main__':
    app.run(debug=True)