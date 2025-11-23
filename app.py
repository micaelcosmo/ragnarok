from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'chave_secreta_ragnarok_rpg'

# Configuração do SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'ragnarok.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==============================================================================
# MODELOS DE BANCO DE DADOS (COM CASCATA CONFIGURADA)
# ==============================================================================

class Modelo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    
    # CASCATA: Deletar Modelo -> Deleta Campos e Personagens (Fichas)
    campos = db.relationship('Campo', backref='modelo', cascade="all, delete-orphan")
    personagens = db.relationship('Personagem', backref='modelo', cascade="all, delete-orphan")

class Campo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    modelo_id = db.Column(db.Integer, db.ForeignKey('modelo.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    
    # CASCATA: Deletar Campo -> Deleta Valores nas fichas
    valores = db.relationship('Valor', backref='campo', cascade="all, delete-orphan")

class Personagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    modelo_id = db.Column(db.Integer, db.ForeignKey('modelo.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    nivel = db.Column(db.Integer, default=1)
    
    # CASCATA: Deletar Personagem -> Deleta seus Valores
    valores = db.relationship('Valor', backref='personagem', cascade="all, delete-orphan")

class Valor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    personagem_id = db.Column(db.Integer, db.ForeignKey('personagem.id'), nullable=False)
    campo_id = db.Column(db.Integer, db.ForeignKey('campo.id'), nullable=False)
    valor_texto = db.Column(db.String(500), nullable=True)

# Inicialização do Banco
with app.app_context():
    db.create_all()
    if not Modelo.query.first():
        m = Modelo(nome="Aventureiro Padrão")
        db.session.add(m)
        db.session.commit()
        db.session.add(Campo(modelo_id=m.id, nome="Classe", tipo="texto"))
        db.session.add(Campo(modelo_id=m.id, nome="Força", tipo="inteiro"))
        db.session.commit()

# ==============================================================================
# ROTAS GERAIS
# ==============================================================================

@app.route('/')
def index():
    personagens = Personagem.query.with_entities(Personagem.id, Personagem.nome).all()
    return render_template('index.html', personagens=personagens)

# ==============================================================================
# ROTAS DE MODELOS (CONFIGURAÇÃO)
# ==============================================================================

@app.route('/configurar_modelos')
def gerenciar_modelos():
    modelos = Modelo.query.all()
    selected_id = request.args.get('modelo_id')
    modelo_selecionado = None
    
    if selected_id:
        # Pequena proteção caso o ID não exista
        modelo_selecionado = Modelo.query.filter_by(id=selected_id).first()

    return render_template('modelos.html', modelos=modelos, modelo_selecionado=modelo_selecionado)

@app.route('/criar_modelo', methods=['POST'])
def criar_modelo():
    nome = request.form.get('nome_modelo')
    if nome:
        novo = Modelo(nome=nome)
        db.session.add(novo)
        db.session.commit()
        return redirect(url_for('gerenciar_modelos', modelo_id=novo.id))
    return redirect(url_for('gerenciar_modelos'))

# --- SUA FUNÇÃO ATUALIZADA ---
@app.route('/deletar_modelo', methods=['POST'])
def deletar_modelo():
    id_modelo = request.form.get('id_modelo')
    print(f"DEBUG: Tentando deletar modelo ID: {id_modelo}") 

    if id_modelo:
        modelo = Modelo.query.get(id_modelo)
        if modelo:
            try:
                # O SQLAlchemy deleta o modelo E as fichas (devido ao cascade configurado lá em cima)
                db.session.delete(modelo)
                db.session.commit()
                print("DEBUG: Modelo e fichas associadas deletados com sucesso!") 
                
                # SUCESSO: Renderiza o refresh para limpar o iframe e atualizar a sidebar
                return render_template('refresh_parent.html')
            
            except Exception as e:
                db.session.rollback()
                print(f"DEBUG ERRO FATAL AO DELETAR: {e}")
        else:
            print("DEBUG: Modelo não encontrado no banco de dados.")
    else:
        print("DEBUG: ID do modelo veio vazio.")
    
    # Se falhar, volta para a tela de modelos
    return redirect(url_for('gerenciar_modelos'))

@app.route('/adicionar_campo', methods=['POST'])
def adicionar_campo():
    modelo_id = request.form.get('modelo_id')
    nome = request.form.get('nome_campo')
    tipo = request.form.get('tipo_campo')
    if modelo_id and nome and tipo:
        campo = Campo(modelo_id=modelo_id, nome=nome, tipo=tipo)
        db.session.add(campo)
        db.session.commit()
        return redirect(url_for('gerenciar_modelos', modelo_id=modelo_id))
    return redirect(url_for('gerenciar_modelos'))

@app.route('/deletar_campo', methods=['POST'])
def deletar_campo():
    campo_id = request.form.get('campo_id')
    modelo_id = request.form.get('modelo_id')
    if campo_id:
        campo = Campo.query.get(campo_id)
        if campo:
            db.session.delete(campo)
            db.session.commit()
    return redirect(url_for('gerenciar_modelos', modelo_id=modelo_id))

# ==============================================================================
# ROTAS DE PERSONAGEM (FICHAS)
# ==============================================================================

@app.route('/novo', methods=['GET', 'POST'])
def novo_personagem():
    if request.method == 'GET' and not request.args.get('modelo_id'):
        modelos = Modelo.query.all()
        return render_template('selecionar_modelo.html', modelos=modelos)

    modelo_id = request.args.get('modelo_id') or request.form.get('modelo_id')
    if not modelo_id:
        return redirect(url_for('novo_personagem'))
    
    modelo = Modelo.query.get_or_404(modelo_id)

    if request.method == 'POST' and 'salvar_ficha' in request.form:
        nome_form = request.form.get('nome')
        if not nome_form or not nome_form.strip():
            nome_form = "Herói Sem Nome"
        
        try: nivel = int(request.form.get('nivel', 1))
        except: nivel = 1

        p = Personagem(nome=nome_form, nivel=nivel, modelo_id=modelo.id)
        db.session.add(p)
        db.session.flush()

        for campo in modelo.campos:
            val = request.form.get(f'campo_{campo.id}')
            if campo.tipo == 'booleano': val = 'Sim' if val == 'on' else 'Não'
            db.session.add(Valor(personagem_id=p.id, campo_id=campo.id, valor_texto=val))
        
        db.session.commit()
        return render_template('refresh_parent.html', id=p.id)
    
    return render_template('form.html', p=None, modelo=modelo, valores={})

# Ponte para links antigos
@app.route('/ficha/<int:id>')
def ver_ficha(id):
    return redirect(url_for('editar_personagem', id=id))

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_personagem(id):
    p = Personagem.query.get_or_404(id)
    
    if request.method == 'POST':
        if 'nivel' in request.form:
            try: p.nivel = int(request.form['nivel'])
            except: pass
        
        for campo in p.modelo.campos:
            val = request.form.get(f'campo_{campo.id}')
            if campo.tipo == 'booleano': val = 'Sim' if val == 'on' else 'Não'
            
            v = Valor.query.filter_by(personagem_id=p.id, campo_id=campo.id).first()
            if v: v.valor_texto = val
            else: db.session.add(Valor(personagem_id=p.id, campo_id=campo.id, valor_texto=val))
            
        db.session.commit()
        return render_template('refresh_parent.html', id=p.id)

    valores_map = {v.campo_id: v.valor_texto for v in p.valores}
    return render_template('ficha.html', p=p, valores=valores_map)

@app.route('/deletar/<int:id>')
def deletar_personagem(id):
    p = Personagem.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return render_template('refresh_parent.html', deleted=True)

if __name__ == '__main__':
    app.run(debug=True)