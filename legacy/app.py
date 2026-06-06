import json
import os
import secrets

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Modelo, Campo, Personagem, Valor


app = Flask(__name__)

# Protótipo arquivado. Segredo NUNCA hardcoded: vem do ambiente ou é efêmero por execução.
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ragnarok.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    """Carrega o usuario logado na sessao."""
    return User.query.get(int(user_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Gerencia o registro de novos usuarios no sistema."""
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
    """Gerencia a autenticacao dos usuarios."""
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
    """Encerra a sessao do usuario atual."""
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
def index():
    """Renderiza o esqueleto principal da aplicacao e lista os personagens."""
    personagens = []
    if current_user.is_authenticated:
        personagens = Personagem.query.filter_by(user_id=current_user.id)\
            .with_entities(Personagem.id, Personagem.nome, Personagem.nivel)\
            .all()
            
    return render_template('index.html', personagens=personagens)


@app.route('/configurar_modelos')
@login_required
def gerenciar_modelos():
    """Lista e permite a visualizacao estrutural dos modelos dinamicos."""
    modelos = Modelo.query.all()
    selected_id = request.args.get('modelo_id')
    modelo_selecionado = Modelo.query.filter_by(id=selected_id).first() if selected_id else None
    return render_template('modelos.html', modelos=modelos, modelo_selecionado=modelo_selecionado)


@app.route('/novo', methods=['GET', 'POST'])
@login_required
def novo_personagem():
    """Gerencia a criacao de uma nova ficha usando o modelo base injetado."""
    modelo = Modelo.query.first()
    
    if not modelo:
        return "Erro: Nenhum modelo de ficha encontrado no banco de dados."

    if request.method == 'POST' and 'salvar_ficha' in request.form:
        nome_form = request.form.get('nome', '').strip()
        nome_form = nome_form if nome_form else "Herói Sem Nome"
        
        try: nivel = int(request.form.get('nivel', 1))
        except ValueError: nivel = 1
            
        try: xp = int(request.form.get('xp', 0))
        except ValueError: xp = 0

        p = Personagem(
            user_id=current_user.id,
            modelo_id=modelo.id,
            nome=nome_form,
            nome_jogador=request.form.get('nome_jogador'),
            raca=request.form.get('raca'),
            classe=request.form.get('classe'),
            nivel=nivel,
            antecedente=request.form.get('antecedente'),
            tendencia=request.form.get('tendencia'),
            xp=xp
        )
        db.session.add(p)
        db.session.flush()

        for campo in modelo.campos:
            val = request.form.get(f'campo_{campo.id}')
            if campo.tipo == 'booleano': 
                val = 'Sim' if val == 'on' else 'Não'
            db.session.add(Valor(personagem_id=p.id, campo_id=campo.id, valor_texto=val))
        
        db.session.commit()
        return render_template('refresh_parent.html', id=p.id)
    
    return render_template('form.html', p=None, modelo=modelo, valores={})


@app.route('/ficha/<int:id>')
@login_required
def ver_ficha(id):
    """Redireciona a visualizacao para a interface de edicao."""
    return redirect(url_for('editar_personagem', id=id))


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_personagem(id):
    """Carrega e processa a atualizacao de uma ficha existente via EAV."""
    p = Personagem.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        if 'nivel' in request.form:
            try: p.nivel = int(request.form['nivel'])
            except ValueError: pass
            
        if 'xp' in request.form:
            try: p.xp = int(request.form['xp'])
            except ValueError: pass
        
        if 'nome_jogador' in request.form: p.nome_jogador = request.form['nome_jogador']
        if 'raca' in request.form: p.raca = request.form['raca']
        if 'classe' in request.form: p.classe = request.form['classe']
        if 'nome' in request.form: p.nome = request.form['nome']
        if 'antecedente' in request.form: p.antecedente = request.form['antecedente']
        if 'tendencia' in request.form: p.tendencia = request.form['tendencia']
        
        for campo in p.modelo_base.campos:
            val = request.form.get(f'campo_{campo.id}')
            if campo.tipo == 'booleano': 
                val = 'Sim' if val == 'on' else 'Não'
            
            v = Valor.query.filter_by(personagem_id=p.id, campo_id=campo.id).first()
            if v: 
                v.valor_texto = val
            else: 
                db.session.add(Valor(personagem_id=p.id, campo_id=campo.id, valor_texto=val))
            
        db.session.commit()
        return render_template('refresh_parent.html', id=p.id)

    valores_map = {v.campo_id: v.valor_texto for v in p.valores}
    return render_template('ficha.html', p=p, valores=valores_map)


@app.route('/deletar/<int:id>')
@login_required
def deletar_personagem(id):
    """Remove a ficha do banco de dados validando propriedade."""
    p = Personagem.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(p)
    db.session.commit()
    return render_template('refresh_parent.html', deleted=True)


def inicializar_banco():
    """Injeta a estrutura unificada das regras de D&D 5e."""
    db.create_all()
    
    modelo_existente = Modelo.query.filter_by(nome="D&D 5e - Livro do Jogador").first()
    if modelo_existente:
        return 

    print("Gerando estrutura padrao do D&D 5e com logica interligada de atributos...")
    novo_modelo = Modelo(
        nome="D&D 5e - Livro do Jogador",
        descricao="Ficha automatizada baseada nas regras oficiais da 5a Edicao."
    )
    db.session.add(novo_modelo)
    db.session.flush()

    estrutura_ficha = {
        "Status Básicos": [
            ("Classe de Armadura (CA)", "inteiro"),
            ("Iniciativa", "inteiro"),
            ("Deslocamento (Speed)", "texto_curto"),
            ("Bônus de Proficiência", "inteiro"), 
            ("Pontos de Vida Máximos", "inteiro"),
            ("Pontos de Vida Atuais", "inteiro"),
            ("Pontos de Vida Temporários", "inteiro"),
            ("Dados de Vida (Hit Dice)", "texto_curto"),
            ("Inspiração", "booleano")
        ],
        "Atributos": [
            ("Força (STR)", "json_atributo"),
            ("Destreza (DEX)", "json_atributo"),
            ("Constituição (CON)", "json_atributo"),
            ("Inteligência (INT)", "json_atributo"),
            ("Sabedoria (WIS)", "json_atributo"),
            ("Carisma (CHA)", "json_atributo")
        ],
        "Salvaguardas (Saving Throws)": [
            ("Salvaguarda: Força", "json_calculado"),
            ("Salvaguarda: Destreza", "json_calculado"),
            ("Salvaguarda: Constituição", "json_calculado"),
            ("Salvaguarda: Inteligência", "json_calculado"),
            ("Salvaguarda: Sabedoria", "json_calculado"),
            ("Salvaguarda: Carisma", "json_calculado")
        ],
        "Perícias (Skills)": [
            ("Acrobacia (Dex)", "json_calculado"),
            ("Arcanismo (Int)", "json_calculado"),
            ("Atletismo (Str)", "json_calculado"),
            ("Atuação (Cha)", "json_calculado"),
            ("Enganação (Cha)", "json_calculado"),
            ("Furtividade (Dex)", "json_calculado"),
            ("História (Int)", "json_calculado"),
            ("Intimidação (Cha)", "json_calculado"),
            ("Intuição (Wis)", "json_calculado"),
            ("Investigação (Int)", "json_calculado"),
            ("Lidar com Animais (Wis)", "json_calculado"),
            ("Medicina (Wis)", "json_calculado"),
            ("Natureza (Int)", "json_calculado"),
            ("Percepção (Wis)", "json_calculado"),
            ("Persuasão (Cha)", "json_calculado"),
            ("Prestidigitação (Dex)", "json_calculado"),
            ("Religião (Int)", "json_calculado"),
            ("Sobrevivência (Wis)", "json_calculado")
        ],
        "Características e Traços": [
            ("Traços de Personalidade", "texto_longo"),
            ("Ideais", "texto_longo"),
            ("Vínculos (Bonds)", "texto_longo"),
            ("Fraquezas (Flaws)", "texto_longo"),
            ("História do Personagem (Backstory)", "texto_longo"),
            ("Características e Talentos", "texto_longo"),
            ("Outras Proficiências e Idiomas", "texto_longo")
        ],
        "Combate e Equipamento": [
            ("Ataques e Magias", "texto_longo"),
            ("Equipamento e Inventário", "texto_longo"),
            ("Dinheiro", "texto_curto")
        ]
    }

    for categoria, lista_campos in estrutura_ficha.items():
        for index, (nome_campo, tipo_campo) in enumerate(lista_campos):
            db.session.add(Campo(
                modelo_id=novo_modelo.id,
                nome=nome_campo,
                tipo=tipo_campo,
                categoria=categoria,
                ordem=index
            ))

    db.session.commit()
    print("Motor de regras do D&D 5e injetado com sucesso!")


if __name__ == '__main__':
    with app.app_context():
        inicializar_banco()
    
    app.run(debug=True)