# seed.py
from app import app
from models import db, Modelo, Campo

def popular_banco():
    """
    Função principal para popular o banco de dados com o modelo do D&D 5e.
    Usamos o app_context() para garantir que o SQLAlchemy saiba qual banco acessar.
    """
    with app.app_context():
        # Verifica se o modelo já existe para não duplicar toda vez que rodar o script
        modelo_existente = Modelo.query.filter_by(nome="D&D 5e - Livro do Jogador").first()
        if modelo_existente:
            print("O modelo 'D&D 5e - Livro do Jogador' já existe no banco de dados.")
            return

        print("Iniciando a criação do modelo D&D 5e...")

        # 1. Cria a entidade base do Modelo
        novo_modelo = Modelo(
            nome="D&D 5e - Livro do Jogador",
            descricao="Ficha completa baseada nas regras oficiais da 5ª Edição."
        )
        db.session.add(novo_modelo)
        db.session.flush() # Dá um flush para pegar o ID do novo_modelo antes do commit final

        # =====================================================================
        # ESTRUTURA DE DADOS DO D&D 5e
        # Dicionário organizando os campos por Categoria e definindo seus tipos
        # =====================================================================
        estrutura_ficha = {
            "Status Básicos": [
                ("Classe de Armadura (CA)", "inteiro"),
                ("Iniciativa", "inteiro"),
                ("Deslocamento (Speed)", "texto_curto"),
                ("Pontos de Vida Máximos", "inteiro"),
                ("Pontos de Vida Atuais", "inteiro"),
                ("Pontos de Vida Temporários", "inteiro"),
                ("Dados de Vida (Hit Dice)", "texto_curto"),
                ("Bônus de Proficiência", "inteiro"),
                ("Inspiração", "booleano")
            ],
            "Atributos": [
                ("Força (STR)", "inteiro"),
                ("Destreza (DEX)", "inteiro"),
                ("Constituição (CON)", "inteiro"),
                ("Inteligência (INT)", "inteiro"),
                ("Sabedoria (WIS)", "inteiro"),
                ("Carisma (CHA)", "inteiro")
            ],
            "Salvaguardas (Saving Throws)": [
                ("Salvaguarda: Força", "inteiro"),
                ("Salvaguarda: Destreza", "inteiro"),
                ("Salvaguarda: Constituição", "inteiro"),
                ("Salvaguarda: Inteligência", "inteiro"),
                ("Salvaguarda: Sabedoria", "inteiro"),
                ("Salvaguarda: Carisma", "inteiro")
            ],
            "Perícias (Skills)": [
                ("Acrobacia (Dex)", "inteiro"),
                ("Arcanismo (Int)", "inteiro"),
                ("Atletismo (Str)", "inteiro"),
                ("Atuação (Cha)", "inteiro"),
                ("Enganação (Cha)", "inteiro"),
                ("Furtividade (Dex)", "inteiro"),
                ("História (Int)", "inteiro"),
                ("Intimidação (Cha)", "inteiro"),
                ("Intuição (Wis)", "inteiro"),
                ("Investigação (Int)", "inteiro"),
                ("Lidar com Animais (Wis)", "inteiro"),
                ("Medicina (Wis)", "inteiro"),
                ("Natureza (Int)", "inteiro"),
                ("Percepção (Wis)", "inteiro"),
                ("Persuasão (Cha)", "inteiro"),
                ("Prestidigitação (Dex)", "inteiro"),
                ("Religião (Int)", "inteiro"),
                ("Sobrevivência (Wis)", "inteiro")
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
                ("Ataques e Magias (Arma | Bônus | Dano/Tipo)", "texto_longo"),
                ("Equipamento e Inventário", "texto_longo"),
                ("Dinheiro (PO, PP, PE, PO, PL)", "texto_curto")
            ],
            "Magias (Grimório)": [
                ("Classe Conjuradora", "texto_curto"),
                ("Atributo de Conjuração", "texto_curto"),
                ("CD de Salvaguarda de Magia", "inteiro"),
                ("Bônus de Ataque de Magia", "inteiro"),
                ("Truques (Cantrips)", "texto_longo"),
                ("Magias de Nível 1", "texto_longo"),
                ("Magias de Nível 2", "texto_longo"),
                ("Magias de Nível 3", "texto_longo"),
                ("Magias de Nível 4", "texto_longo"),
                ("Magias de Nível 5", "texto_longo"),
                ("Magias de Nível 6", "texto_longo"),
                ("Magias de Nível 7", "texto_longo"),
                ("Magias de Nível 8", "texto_longo"),
                ("Magias de Nível 9", "texto_longo")
            ]
        }

        # 2. Percorre o dicionário para criar os campos dinâmicos atrelados ao modelo
        for categoria, lista_campos in estrutura_ficha.items():
            for index, (nome_campo, tipo_campo) in enumerate(lista_campos):
                novo_campo = Campo(
                    modelo_id=novo_modelo.id,
                    nome=nome_campo,
                    tipo=tipo_campo,
                    categoria=categoria,
                    ordem=index # Garante que a ordem visual respeite a ordem da lista acima
                )
                db.session.add(novo_campo)

        # 3. Salva tudo de forma definitiva no banco
        db.session.commit()
        print("Sucesso! Modelo do D&D 5e criado com todos os campos organizados.")

if __name__ == '__main__':
    popular_banco()