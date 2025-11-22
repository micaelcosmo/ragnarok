from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configuração do SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'ragnarok.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELO (Tabela) ---
class Personagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    classe = db.Column(db.String(50))
    raca = db.Column(db.String(50))
    nivel = db.Column(db.Integer, default=1)
    # Atributos
    forca = db.Column(db.Integer, default=10)
    destreza = db.Column(db.Integer, default=10)
    constituicao = db.Column(db.Integer, default=10)
    inteligencia = db.Column(db.Integer, default=10)
    sabedoria = db.Column(db.Integer, default=10)
    carisma = db.Column(db.Integer, default=10)
    
    historia = db.Column(db.Text, nullable=True)

# Cria o banco se não existir
with app.app_context():
    db.create_all()

# --- ROTAS ---

@app.route('/')
def index():
    # Busca apenas ID e Nome para a sidebar (leveza)
    personagens = Personagem.query.with_entities(Personagem.id, Personagem.nome).all()
    return render_template('index.html', personagens=personagens)

@app.route('/ficha/<int:id>')
def ver_ficha(id):
    p = Personagem.query.get_or_404(id)
    return render_template('ficha.html', p=p)

@app.route('/novo', methods=['GET', 'POST'])
def novo_personagem():
    if request.method == 'POST':
        # Captura dos dados simplificada
        p = Personagem(
            nome=request.form['nome'],
            classe=request.form['classe'],
            raca=request.form['raca'],
            nivel=request.form['nivel'],
            forca=request.form['forca'],
            destreza=request.form['destreza'],
            constituicao=request.form['constituicao'],
            inteligencia=request.form['inteligencia'],
            sabedoria=request.form['sabedoria'],
            carisma=request.form['carisma'],
            historia=request.form['historia']
        )
        db.session.add(p)
        db.session.commit()
        # Renderiza um template especial para atualizar a sidebar
        return render_template('refresh_parent.html', id=p.id)
    
    return render_template('form.html', p=None)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_personagem(id):
    p = Personagem.query.get_or_404(id)
    
    if request.method == 'POST':
        p.nome = request.form['nome']
        p.classe = request.form['classe']
        p.raca = request.form['raca']
        p.nivel = request.form['nivel']
        p.forca = request.form['forca']
        p.destreza = request.form['destreza']
        p.constituicao = request.form['constituicao']
        p.inteligencia = request.form['inteligencia']
        p.sabedoria = request.form['sabedoria']
        p.carisma = request.form['carisma']
        p.historia = request.form['historia']
        
        db.session.commit()
        return render_template('refresh_parent.html', id=p.id)

    return render_template('form.html', p=p)

@app.route('/deletar/<int:id>')
def deletar_personagem(id):
    p = Personagem.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return render_template('refresh_parent.html', deleted=True)

if __name__ == '__main__':
    app.run(debug=True)