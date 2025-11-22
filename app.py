from flask import Flask, render_template

app = Flask(__name__)

# Simulando seu Banco de Dados por enquanto
# Depois você troca isso por uma chamada SQL ou ORM (SQLAlchemy)
FICHAS_MOCK = [
    {"id": 1, "nome": "Thor", "classe": "Guerreiro", "nivel": 99},
    {"id": 2, "nome": "Loki", "classe": "Mago", "nivel": 85},
    {"id": 3, "nome": "Odin", "classe": "Paladino", "nivel": 100},
]

@app.route('/')
def home():
    # Aqui acontece a mágica: passamos a lista 'FICHAS_MOCK' 
    # para o template com o nome 'fichas'
    return render_template('index.html', fichas=FICHAS_MOCK)
# No seu app.py
@app.route('/fichas')
def fichas():
    # Dados mockados (simulando retorno do banco)
    dados_fichas = [
        {
            "nome": "Micael",
            "classe": "Lord Knight",
            "nivel": 99,
            "hp": 15400,
            "sp": 450,
            "atributos": {"str": 99, "agi": 76, "vit": 60, "int": 10, "dex": 54, "luk": 1},
            "img_url": "https://static.wikia.nocookie.net/ragnarok_gamepedia_en/images/6/66/Lord_Knight.png" 
        },
        {
            "nome": "Cosmo",
            "classe": "High Wizard",
            "nivel": 98,
            "hp": 6500,
            "sp": 2200,
            "atributos": {"str": 1, "agi": 9, "vit": 40, "int": 99, "dex": 99, "luk": 1},
            "img_url": "https://static.wikia.nocookie.net/ragnarok_gamepedia_en/images/2/22/High_Wizard.png"
        }
    ]
    return render_template('fichas.html', fichas=dados_fichas)
if __name__ == '__main__':
    app.run(debug=True)