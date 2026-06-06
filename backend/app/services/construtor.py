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

        mods = derivado["modificadores"]
        bp = derivado["bonus_proficiencia"]
        derivado["ca"] = self._calcular_ca(personagem, mods, final["ca_bonus"])
        derivado["ataques_equipados"] = self._ataques(personagem, mods, bp)
        derivado["atributos_final"] = final["atributos"]
        derivado["concedido"] = final["concedido"]
        derivado["recursos"] = final["recursos"]
        derivado["sentidos"] = final["sentidos"]
        derivado["idiomas_concedidos"] = final["idiomas"]
        derivado["proficiencias_concedidas"] = final["proficiencias_texto"]
        derivado["pericias_proficientes_final"] = final["pericias_proficientes"]
        derivado["salvaguardas_proficientes_final"] = final["salvaguardas_proficientes"]
        return derivado

    def _calcular_ca(self, personagem, mods, ca_bonus_fontes):
        """
        CA = armadura equipada (base + DES limitado + bônus mágico) OU CA base manual;
        + ajuste manual (`ca_ajuste`) + bônus de outras fontes.
        """
        ajuste = int(personagem.ca_ajuste or 0) + int(ca_bonus_fontes or 0)
        armadura = None
        if personagem.armadura_equipada_id:
            from app.models.items import Armadura
            armadura = Armadura.query.get(personagem.armadura_equipada_id)
        if armadura is None:
            return int(personagem.ca or 10) + ajuste
        ca = int(armadura.ca_base or 10)
        if armadura.ca_soma_des:
            des = mods["des"]
            if armadura.ca_des_max is not None:
                des = min(des, int(armadura.ca_des_max))
            ca += des
        ca += int(armadura.ca_bonus or 0) + int(armadura.bonus_magico or 0)
        return ca + ajuste

    def _ataques(self, personagem, mods, bp):
        """Monta a lista de ataques das armas equipadas (bônus de acerto + dano)."""
        ids = personagem.armas_equipadas or []
        if not ids:
            return []
        from app.models.items import Arma
        ataques = []
        for arma in Arma.query.filter(Arma.id.in_(ids)).all():
            efeito = (arma.efeitos or {}).get("ataque", {})
            # Acuidade ou arma à distância usam DES; senão FOR.
            usa_des = efeito.get("acuidade") or arma.alcance == "à distância"
            mod = mods["des"] if usa_des else mods["for"]
            bonus_acerto = mod + bp + int(arma.bonus_magico or 0)
            ataques.append({
                "id": arma.id,
                "nome": arma.nome,
                "bonus_acerto": bonus_acerto,
                "dano": arma.dano,
                "tipo_dano": arma.tipo_dano,
                "bonus_dano": mod + int(arma.bonus_magico or 0),
            })
        return ataques


def construir_derivados(personagem):
    """Atalho funcional."""
    return ConstrutorDeFicha(personagem).construir()
