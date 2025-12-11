from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Modelo, Campo, Personagem, Valor

app = Flask(__name__)

# CONFIGURAÇÕES
app.config['SECRET_KEY'] = 'uma_chave_secreta_muito_segura_aqui' # Necessário para sessões
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ragnarok.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# INICIALIZAÇÃO
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login' # Nome da função da rota de login
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==============================================================================
# ROTAS DE AUTENTICAÇÃO
# ==============================================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        
        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Email já cadastrado!')
            return redirect(url_for('register'))
        
        new_user = User(email=email, name=name)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registro realizado com sucesso! Faça login.')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Verifique seus dados e tente novamente.')
            return redirect(url_for('login'))
            
        login_user(user)
        return redirect(url_for('index'))
        
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- SUAS ROTAS EXISTENTES (Index, Fichas, etc) ---

# @app.route('/')
# @login_required # Opcional: Exige login para ver a home
# def index():
#     return render_template('index.html', user=current_user)

# ==============================================================================
# ROTAS DE INDEX
# ==============================================================================

@app.route('/')
def index():
    # ATUALIZAÇÃO AQUI: Adicionado Personagem.nivel na consulta
    personagens = Personagem.query.with_entities(Personagem.id, Personagem.nome, Personagem.nivel).all()
    return render_template('index.html', personagens=personagens)

# ==============================================================================
# ROTAS DE MODELOS (FICHAS)
# ==============================================================================

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
    print(f"DEBUG: Tentando deletar modelo ID: {id_modelo}") 

    if id_modelo:
        modelo = Modelo.query.get(id_modelo)
        if modelo:
            try:
                # O SQLAlchemy deleta o modelo E as fichas (devido ao cascade configurado no models.py)
                db.session.delete(modelo)
                db.session.commit()
                print("DEBUG: Modelo e fichas associadas deletados com sucesso!") 
                
                return render_template('refresh_parent.html')
            
            except Exception as e:
                db.session.rollback()
                print(f"DEBUG ERRO FATAL AO DELETAR: {e}")
        else:
            print("DEBUG: Modelo não encontrado no banco de dados.")
    else:
        print("DEBUG: ID do modelo veio vazio.")
    
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

# Lembre-se de passar `user=current_user` ou usar `current_user` direto no Jinja2
# para mostrar/esconder elementos na barra lateral.

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Cria a tabela users se não existir
    app.run(debug=True)