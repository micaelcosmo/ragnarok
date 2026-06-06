"""
ConstrutorDeFicha — resolve as fontes (raça/classe/antecedente/talentos) do banco,
soma seus `efeitos` sobre a camada base/manual do personagem e devolve a ficha final.

POO: encapsula a montagem. Usa o módulo puro `app.rules.efeitos` para a soma (testável) e
`app.rules.dnd5e` para os derivados 5E.
"""
from app.rules import dnd5e, efeitos as ef


class ConstrutorDeFicha:
    """Monta a ficha final (base + fontes) de um personagem."""

    def __init__(self, personagem):
        self.personagem = personagem

    def _fontes_efeitos(self):
        """Coleta os `efeitos` das fontes ativas do personagem (consulta o catálogo)."""
        from app.models.reference import Antecedente, Classe, Raca, Talento

        fontes = []
        if self.personagem.raca_slug:
            raca = Raca.query.filter_by(slug=self.personagem.raca_slug).first()
            if raca and raca.efeitos:
                fontes.append(raca.efeitos)
        if self.personagem.classe_slug:
            classe = Classe.query.filter_by(slug=self.personagem.classe_slug).first()
            if classe and classe.efeitos:
                fontes.append(classe.efeitos)
        if self.personagem.antecedente_slug:
            antecedente = Antecedente.query.filter_by(slug=self.personagem.antecedente_slug).first()
            if antecedente and antecedente.efeitos:
                fontes.append(antecedente.efeitos)
        for slug in (self.personagem.talentos or []):
            talento = Talento.query.filter_by(slug=slug).first()
            if talento and talento.efeitos:
                fontes.append(talento.efeitos)
        return fontes

    def construir(self):
        """Devolve o bloco de derivados enriquecido (com fontes aplicadas)."""
        personagem = self.personagem
        base = {
            "atributos": personagem.atributos_dict(),
            "pericias_proficientes": personagem.pericias_proficientes or [],
            "salvaguardas_proficientes": personagem.salvaguardas_proficientes or [],
            "iniciativa_bonus": personagem.iniciativa_bonus or 0,
        }
        final = ef.aplicar(base, self._fontes_efeitos())

        derivado = dnd5e.ficha_derivada(
            final["atributos"],
            personagem.nivel,
            pericias_proficientes=final["pericias_proficientes"],
            salvaguardas_proficientes=final["salvaguardas_proficientes"],
            atributo_conjuracao=personagem.atributo_conjuracao,
            iniciativa_bonus_extra=final["iniciativa_extra"],
        )

        # CA final = base + ajuste manual + bônus de fontes (armadura/escudo vêm na Fase 3).
        derivado["ca"] = int(personagem.ca or 10) + int(personagem.ca_ajuste or 0) + final["ca_bonus"]
        derivado["atributos_final"] = final["atributos"]
        derivado["concedido"] = final["concedido"]
        derivado["recursos"] = final["recursos"]
        derivado["sentidos"] = final["sentidos"]
        derivado["idiomas_concedidos"] = final["idiomas"]
        derivado["proficiencias_concedidas"] = final["proficiencias_texto"]
        derivado["pericias_proficientes_final"] = final["pericias_proficientes"]
        derivado["salvaguardas_proficientes_final"] = final["salvaguardas_proficientes"]
        return derivado


def construir_derivados(personagem):
    """Atalho funcional."""
    return ConstrutorDeFicha(personagem).construir()
