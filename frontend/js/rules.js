// Espelho leve do motor de regras (apenas para preview no cliente).
// A fonte da verdade é o backend (campo `derivados`).

export const ATRIBUTOS = ['for', 'des', 'con', 'int', 'sab', 'car'];

export const NOMES_ATRIBUTOS = {
  for: 'Força', des: 'Destreza', con: 'Constituição',
  int: 'Inteligência', sab: 'Sabedoria', car: 'Carisma',
};

export const PERICIAS = {
  Acrobacia: 'des', 'Adestrar Animais': 'sab', Arcanismo: 'int', Atletismo: 'for',
  Atuação: 'car', Enganação: 'car', Furtividade: 'des', História: 'int',
  Intimidação: 'car', Intuição: 'sab', Investigação: 'int', Medicina: 'sab',
  Natureza: 'int', Percepção: 'sab', Persuasão: 'car', Prestidigitação: 'des',
  Religião: 'int', Sobrevivência: 'sab',
};

export function modificador(valor) {
  return Math.floor(((Number(valor) || 10) - 10) / 2);
}

export function bonusProficiencia(nivel) {
  const limitado = Math.min(20, Math.max(1, Number(nivel) || 1));
  return 2 + Math.floor((limitado - 1) / 4);
}
