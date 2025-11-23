# ⚔️ Ragnarok - Grimório Digital

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-07405e?style=for-the-badge&logo=sqlite&logoColor=white)

> *"Toda lenda começa com uma escolha..."*

**Ragnarok** é um gerenciador de fichas de RPG **agnóstico de sistema**. Diferente de plataformas presas ao D&D ou Pathfinder, o Ragnarok permite que o mestre ou jogador **crie seus próprios modelos de ficha**, definindo dinamicamente quais campos, atributos e tipos de dados compõem o sistema de regras.

Construído com **Python (Flask)** e **SQLite**, focado em uma interface imersiva estilo "Dark Fantasy/Pergaminho".

---

## 📸 Visão Geral

O sistema funciona através de um **Iframe Central** controlado por uma **Barra Lateral**, garantindo navegação fluida sem recarregamentos desnecessários da interface principal.

| Configuração de Modelos | Ficha de Personagem |
|:---:|:---:|
| *Crie templates personalizados (D&D, Tormenta, CoC)* | *Preenchimento dinâmico e visualização imersiva* |
| ![Modelos](https://placehold.co/400x250/2c241b/d4af37?text=Criacao+de+Modelos) | ![Ficha](https://placehold.co/400x250/f4e4bc/5c4033?text=Ficha+de+Personagem) |

---

## ✨ Funcionalidades Principais

### 🛠️ Sistema de Modelos Dinâmicos (Meta-Ficha)
A grande força do projeto. O usuário não está preso a campos fixos.
- **Criação Customizada:** Defina o nome do sistema (ex: "Vampiro: A Máscara", "Call of Cthulhu").
- **Tipagem de Campos:** Adicione campos dinamicamente com validação:
  - `Texto Curto` (ex: Nome, Classe, Raça)
  - `Inteiro` (ex: Força, Destreza, PV)
  - `Texto Longo` (ex: Inventário, Background)
  - `Booleano` (ex: Inspiração, Está Vivo?)
- **Integridade Referencial:** O sistema utiliza `Cascades` do SQLAlchemy. Ao excluir um modelo, todas as fichas e valores associados são limpos automaticamente.

### 📜 Gerenciador de Personagens
- **Herança de Modelo:** Ao criar um herói, o sistema carrega a estrutura do modelo escolhido.
- **Modo Leitura vs. Edição:** Interface limpa para jogar e formulário robusto para editar valores.
- **Navegação Fluida:** Feedback visual de carregamento e atualização automática da lista de heróis.

---

## 🚀 Instalação e Execução

### 1. Clone o repositório
```bash
git clone [https://github.com/micaelcosmo/ragnarok.git](https://github.com/micaelcosmo/ragnarok.git)
cd ragnarok
2. Prepare o Ambiente Virtual
Bash

# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
3. Instale as dependências
Bash

pip install -r requirements.txt
4. Execute o Grimório
Bash

python app.py
O servidor iniciará em http://127.0.0.1:5000.

Nota: O banco de dados ragnarok.db será criado automaticamente na primeira execução com um modelo de exemplo ("Aventureiro Padrão").

🏗️ Estrutura do Projeto
O projeto segue o padrão MTV (Model-Template-View) do Flask:

Plaintext

ragnarok/
├── app.py                 # Controller (Rotas) e Models (SQLAlchemy)
├── ragnarok.db            # Banco de dados SQLite (Auto-gerado)
├── requirements.txt       # Dependências do projeto
├── static/
│   └── css/
│       └── style.css      # Estilização (Temas Dark/Parchment com CSS Variables)
└── templates/
    ├── index.html         # Layout base + Sidebar (Container do Iframe)
    ├── ficha.html         # Visualização/Edição do Personagem
    ├── modelos.html       # CRUD de Modelos e Campos
    ├── form.html          # Formulário de Criação de Personagem
    ├── selecionar_modelo.html # Passo 1 da criação
    └── refresh_parent.html # Utilitário de atualização de UI (ponte iframe-pai)
🎨 Design System
O projeto utiliza CSS Variables para facilitar a manutenção e consistência visual:

Tema Dark (Interface Externa): #1a1a1a (Fundo), #2c241b (Painéis).

Tema Pergaminho (Fichas): #f4e4bc (Papel), #8a6d3b (Detalhes Dourados).

Tipografia: Cinzel (Títulos Medievais) e Lato (Legibilidade).

🤝 Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests para adicionar novos tipos de campos (ex: Select Box, Rolagem de Dados) ou melhorar a interface.

<div align="center"> <small>Desenvolvido por <strong>Micael Cosmo</strong></small> </div>