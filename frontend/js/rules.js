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

// Descrições curtas para tooltips (apenas leitura, não atrapalham digitação).
export const DESC_ATRIBUTOS = {
  for: 'Força física: ataques corpo a corpo, carregar peso, Atletismo.',
  des: 'Destreza: CA, iniciativa, ataques à distância, Acrobacia/Furtividade.',
  con: 'Constituição: pontos de vida e resistência física.',
  int: 'Inteligência: conhecimento, magia arcana, Arcanismo/Investigação.',
  sab: 'Sabedoria: percepção e intuição, magia divina, Percepção/Medicina.',
  car: 'Carisma: presença e influência social, Persuasão/Intimidação.',
};

export const DESC_PERICIAS = {
  Acrobacia: 'Equilíbrio, manobras e acrobacias (Des).',
  'Adestrar Animais': 'Acalmar e lidar com animais (Sab).',
  Arcanismo: 'Conhecimento sobre magia e o arcano (Int).',
  Atletismo: 'Escalar, nadar, saltar e força física (For).',
  Atuação: 'Apresentações artísticas para uma plateia (Car).',
  Enganação: 'Mentir e enganar de forma convincente (Car).',
  Furtividade: 'Mover-se sem ser visto ou ouvido (Des).',
  História: 'Conhecimento de eventos e lendas (Int).',
  Intimidação: 'Coagir por ameaças e presença (Car).',
  Intuição: 'Perceber intenções e mentiras (Sab).',
  Investigação: 'Deduzir pistas e procurar detalhes (Int).',
  Medicina: 'Estabilizar feridos e diagnosticar (Sab).',
  Natureza: 'Conhecimento de terreno, plantas e clima (Int).',
  Percepção: 'Notar o que está ao redor (Sab).',
  Persuasão: 'Influenciar com tato e cordialidade (Car).',
  Prestidigitação: 'Truques manuais e furto (Des).',
  Religião: 'Conhecimento de divindades e ritos (Int).',
  Sobrevivência: 'Rastrear, caçar e orientar-se (Sab).',
};

export const DESC_COMBATE = {
  CA: 'Classe de Armadura: dificuldade para acertá-lo em combate.',
  Iniciativa: 'Ordem de agir no combate (modificador de Destreza).',
  Deslocamento: 'Distância que você percorre por turno.',
  Proficiência: 'Bônus de proficiência: somado ao que você é treinado.',
  Salvaguarda: 'Resistência: teste para evitar ou reduzir um efeito.',
  PassivaPercepcao: 'Percepção passiva: 10 + valor de Percepção (notar sem rolar).',
};

export function modificador(valor) {
  return Math.floor(((Number(valor) || 10) - 10) / 2);
}

export function bonusProficiencia(nivel) {
  const limitado = Math.min(20, Math.max(1, Number(nivel) || 1));
  return 2 + Math.floor((limitado - 1) / 4);
}
