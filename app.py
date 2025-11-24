from flask import Flask, render_template, request, redirect, url_for, flash
import os

# Importa o objeto db e as classes do arquivo models.py
from models import db, Modelo, Campo, Personagem, Valor

app = Flask(__name__)
app.secret_key = 'chave_secreta_ragnarok_rpg'

# Configuração do SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'ragnarok.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Conecta o objeto db ao app
db.init_app(app)

# Inicialização do Banco e Seed
with app.app_context():
    db.create_all()
    if not Modelo.query.first():
        m = Modelo(nome="Aventureiro Padrão")
        db.session.add(m)
        db.session.commit()
        # Removido "Classe" daqui, pois agora é fixo na tabela Personagem
        db.session.add(Campo(modelo_id=m.id, nome="História", tipo="textarea"))
        db.session.add(Campo(modelo_id=m.id, nome="Força", tipo="inteiro"))
        db.session.commit()

# ==============================================================================
# ROTAS GERAIS E MODELOS
# ==============================================================================

@app.route('/')
def index():
    personagens = Personagem.query.with_entities(Personagem.id, Personagem.nome, Personagem.nivel).all()
    return render_template('index.html', personagens=personagens)

@app.route('/configurar_modelos')
def gerenciar_modelos():
    modelos = Modelo.query.all()
    selected_id = request.args.get('modelo_id')
    modelo_selecionado = None
    if selected_id:
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

@app.route('/deletar_modelo', methods=['POST'])
def deletar_modelo():
    id_modelo = request.form.get('id_modelo')
    if id_modelo:
        modelo = Modelo.query.get(id_modelo)
        if modelo:
            try:
                db.session.delete(modelo)
                db.session.commit()
                return render_template('refresh_parent.html')
            except Exception as e:
                db.session.rollback()
                print(f"Erro ao deletar: {e}")
    return redirect(url_for('gerenciar_modelos'))

@app.route('/adicionar_campo', methods=['POST'])
def adicionar_campo():
    modelo_id = request.form.get('modelo_id')
    nome = request.form.get('nome_campo')
    tipo = request.form.get('tipo_campo')
    if modelo_id and nome and tipo:
        db.session.add(Campo(modelo_id=modelo_id, nome=nome, tipo=tipo))
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

        # Criação com os NOVOS CAMPOS FIXOS
        p = Personagem(
            nome=nome_form,
            nome_jogador=request.form.get('nome_jogador'),
            raca=request.form.get('raca'),
            classe=request.form.get('classe'),
            nivel=nivel,
            modelo_id=modelo.id
        )
        db.session.add(p)
        db.session.flush()

        for campo in modelo.campos:
            val = request.form.get(f'campo_{campo.id}')
            if campo.tipo == 'booleano': val = 'Sim' if val == 'on' else 'Não'
            db.session.add(Valor(personagem_id=p.id, campo_id=campo.id, valor_texto=val))
        
        db.session.commit()
        return render_template('refresh_parent.html', id=p.id)
    
    return render_template('form.html', p=None, modelo=modelo, valores={})

@app.route('/ficha/<int:id>')
def ver_ficha(id):
    return redirect(url_for('editar_personagem', id=id))

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_personagem(id):
    p = Personagem.query.get_or_404(id)
    
    if request.method == 'POST':
        # Atualiza CAMPOS FIXOS
        if 'nivel' in request.form:
            try: p.nivel = int(request.form['nivel'])
            except: pass
        
        if 'nome_jogador' in request.form: p.nome_jogador = request.form['nome_jogador']
        if 'raca' in request.form: p.raca = request.form['raca']
        if 'classe' in request.form: p.classe = request.form['classe']
        
        # Atualiza CAMPOS DINÂMICOS
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