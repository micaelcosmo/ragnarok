from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'chave_secreta_para_flash_messages' # Necessário para feedback visual

# Configuração do SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'ragnarok.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==============================================================================
# MODELOS DE BANCO DE DADOS (COM CASCADES CORRIGIDOS)
# ==============================================================================

class Modelo(db.Model):
    """Define um template de ficha (ex: D&D, Tormenta, Call of Cthulhu)"""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    # Se deletar o modelo, deleta os campos e os personagens associados
    campos = db.relationship('Campo', backref='modelo', cascade="all, delete-orphan")
    personagens = db.relationship('Personagem', backref='modelo', cascade="all, delete-orphan")

class Campo(db.Model):
    """Define os campos disponíveis em um modelo"""
    id = db.Column(db.Integer, primary_key=True)
    modelo_id = db.Column(db.Integer, db.ForeignKey('modelo.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False) # 'texto', 'inteiro', 'booleano'
    # FIX: Se deletar o campo, deleta os valores preenchidos nas fichas
    valores = db.relationship('Valor', backref='campo', cascade="all, delete-orphan")

class Personagem(db.Model):
    """O personagem em si, vinculado a um modelo"""
    id = db.Column(db.Integer, primary_key=True)
    modelo_id = db.Column(db.Integer, db.ForeignKey('modelo.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    nivel = db.Column(db.Integer, default=1)
    valores = db.relationship('Valor', backref='personagem', cascade="all, delete-orphan")

class Valor(db.Model):
    """O valor preenchido para um campo específico"""
    id = db.Column(db.Integer, primary_key=True)
    personagem_id = db.Column(db.Integer, db.ForeignKey('personagem.id'), nullable=False)
    campo_id = db.Column(db.Integer, db.ForeignKey('campo.id'), nullable=False)
    valor_texto = db.Column(db.String(500), nullable=True)

# Inicialização do Banco
with app.app_context():
    db.create_all()
    if not Modelo.query.first():
        # Seed inicial para não abrir vazio
        m = Modelo(nome="Aventureiro Padrão")
        db.session.add(m)
        db.session.flush()
        db.session.add(Campo(modelo_id=m.id, nome="Classe", tipo="texto"))
        db.session.add(Campo(modelo_id=m.id, nome="Força", tipo="inteiro"))
        db.session.add(Campo(modelo_id=m.id, nome="História", tipo="textarea")) # Mudei para textarea
        db.session.commit()

# ==============================================================================
# ROTAS GERAIS
# ==============================================================================

@app.route('/')
def index():
    personagens = Personagem.query.with_entities(Personagem.id, Personagem.nome).all()
    return render_template('index.html', personagens=personagens)

# ==============================================================================
# ROTAS DE GERENCIAMENTO DE MODELOS (CORRIGIDAS)
# ==============================================================================

@app.route('/configurar_modelos')
def gerenciar_modelos():
    """Renderiza a tela principal de configuração."""
    modelos = Modelo.query.all()
    
    # Captura o ID da query string para manter o modelo aberto após edição
    # Ex: /configurar_modelos?modelo_id=5
    selected_id = request.args.get('modelo_id')
    modelo_selecionado = None
    
    if selected_id:
        modelo_selecionado = Modelo.query.get(selected_id)

    return render_template('modelos.html', modelos=modelos, modelo_selecionado=modelo_selecionado, selected_id=selected_id)

@app.route('/criar_modelo', methods=['POST'])
def criar_modelo():
    """Cria um novo grimório (modelo)."""
    nome = request.form.get('nome_modelo')
    if nome:
        novo = Modelo(nome=nome)
        db.session.add(novo)
        db.session.commit()
        # Redireciona já abrindo o novo modelo criado
        return redirect(url_for('gerenciar_modelos', modelo_id=novo.id))
    return redirect(url_for('gerenciar_modelos'))

@app.route('/deletar_modelo', methods=['POST'])
def deletar_modelo():
    """Exclui um modelo e todos os dados associados."""
    id_modelo = request.form.get('id_modelo')
    if id_modelo:
        modelo = Modelo.query.get(id_modelo)
        if modelo:
            db.session.delete(modelo)
            db.session.commit()
    return redirect(url_for('gerenciar_modelos'))

@app.route('/adicionar_campo', methods=['POST'])
def adicionar_campo():
    """Adiciona um campo a um modelo existente."""
    # Nota: Você precisará ajustar seu HTML 'modelos.html' para postar para cá
    # ou manter a lógica antiga. Recomendo usar esta rota dedicada.
    modelo_id = request.form.get('modelo_id') # Certifique-se de ter um input hidden com isso
    nome = request.form.get('nome_campo') # Ou ajustar conforme seu form
    tipo = request.form.get('tipo_campo')
    
    if modelo_id and nome and tipo:
        campo = Campo(modelo_id=modelo_id, nome=nome, tipo=tipo)
        db.session.add(campo)
        db.session.commit()
        return redirect(url_for('gerenciar_modelos', modelo_id=modelo_id))
        
    return redirect(url_for('gerenciar_modelos'))

@app.route('/deletar_campo', methods=['POST'])
def deletar_campo():
    """Rota que estava faltando: Exclui um campo específico."""
    id_modelo = request.form.get('id_modelo')
    nome_campo = request.form.get('nome_campo')
    
    # Tenta buscar pelo ID se vier, ou pelo nome e modelo_id
    if id_modelo and nome_campo:
        campo = Campo.query.filter_by(modelo_id=id_modelo, nome=nome_campo).first()
        if campo:
            db.session.delete(campo)
            db.session.commit()
            
    # Retorna para a tela de configuração mantendo o modelo aberto
    return redirect(url_for('gerenciar_modelos', modelo_id=id_modelo))

# ==============================================================================
# ROTAS DE PERSONAGEM
# ==============================================================================

@app.route('/novo', methods=['GET', 'POST'])
def novo_personagem():
    # Se for GET, apenas mostra seleção
    if request.method == 'GET':
        modelos = Modelo.query.all()
        # Verifica se já escolheu o modelo na URL
        modelo_id = request.args.get('modelo_id')
        if modelo_id:
            modelo = Modelo.query.get_or_404(modelo_id)
            return render_template('form.html', p=None, modelo=modelo)
        return render_template('selecionar_modelo.html', modelos=modelos)

    # Se for POST (Salvando a ficha)
    modelo_id = request.form.get('modelo_id')
    modelo = Modelo.query.get_or_404(modelo_id)

    p = Personagem(
        nome=request.form['nome'],
        nivel=request.form['nivel'],
        modelo_id=modelo.id
    )
    db.session.add(p)
    db.session.flush()

    for campo in modelo.campos:
        chave_form = f'campo_{campo.id}'
        valor_bruto = request.form.get(chave_form)
        
        if campo.tipo == 'booleano':
            valor_bruto = 'Sim' if valor_bruto == 'on' else 'Não'
        
        v = Valor(personagem_id=p.id, campo_id=campo.id, valor_texto=valor_bruto)
        db.session.add(v)
    
    db.session.commit()
    return render_template('refresh_parent.html', id=p.id)

@app.route('/ficha/<int:id>')
def ver_ficha(id):
    p = Personagem.query.get_or_404(id)
    valores_map = {v.campo_id: v.valor_texto for v in p.valores}
    return render_template('ficha.html', p=p, valores=valores_map)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_personagem(id):
    p = Personagem.query.get_or_404(id)
    modelo = p.modelo

    if request.method == 'POST':
        p.nome = request.form['nome']
        p.nivel = request.form['nivel']
        
        for campo in modelo.campos:
            chave_form = f'campo_{campo.id}'
            valor_bruto = request.form.get(chave_form)

            if campo.tipo == 'booleano':
                valor_bruto = 'Sim' if valor_bruto == 'on' else 'Não'
            
            v = Valor.query.filter_by(personagem_id=p.id, campo_id=campo.id).first()
            if v:
                v.valor_texto = valor_bruto
            else:
                v = Valor(personagem_id=p.id, campo_id=campo.id, valor_texto=valor_bruto)
                db.session.add(v)

        db.session.commit()
        return render_template('refresh_parent.html', id=p.id)

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