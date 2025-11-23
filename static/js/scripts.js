// ==========================================
// script.js - Lógica da Ficha de Personagem
// ==========================================

// Variáveis do DOM
const sheetContainer = document.getElementById('sheetContainer');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const toggleEditBtn = document.getElementById('toggleEditBtn');
const addCharacterBtn = document.getElementById('addCharacterBtn');

// Variáveis de Estado
let characters = [];
let currentIndex = 0;
let isEditing = false;
let db, appId, userId;

// Referência à coleção pública de fichas
const CHARACTER_COLLECTION_PATH = 'ragnarok_characters';

/**
 * Função de inicialização chamada pelo script do index.html após autenticação.
 */
window.initApp = (firestoreDb, authUserId, currentAppId) => {
    // Importa as funções do Firestore globalmente
    db = firestoreDb;
    userId = authUserId;
    appId = currentAppId;

    // Exibe os botões de controle
    if (toggleEditBtn) toggleEditBtn.classList.remove('hidden');
    if (addCharacterBtn) addCharacterBtn.classList.remove('hidden');
    if (toggleEditBtn) toggleEditBtn.disabled = false;
    if (addCharacterBtn) addCharacterBtn.disabled = false;

    setupFirestoreListener();
    setupEventListeners();
};

/**
 * Configura o listener em tempo real para as fichas no Firestore.
 */
const setupFirestoreListener = () => {
    if (typeof collection === 'undefined' || !db || !appId) return;

    const { collection, query, onSnapshot } = window; // Garante acesso às globais do Firebase

    const characterRef = collection(db, `artifacts/${appId}/public/data/${CHARACTER_COLLECTION_PATH}`);
    const q = query(characterRef);

    onSnapshot(q, (snapshot) => {
        const fetchedCharacters = [];
        snapshot.forEach((doc) => {
            fetchedCharacters.push({ id: doc.id, ...doc.data() });
        });
        
        characters = fetchedCharacters;
        
        // Ajuste de índice se necessário
        if (currentIndex >= characters.length && characters.length > 0) {
            currentIndex = characters.length - 1;
        } else if (characters.length === 0) {
            currentIndex = 0;
        }

        updateSheetDisplay(true); // Atualiza sem animação
        console.log(`Grimório atualizado: ${characters.length} fichas.`);

        if (characters.length === 0) {
            sheetContainer.innerHTML = `<p class="cinzel-font text-2xl font-bold text-center text-gray-800 mt-10">Nenhum herói encontrado.<br><span class="text-lg font-sans font-normal">Clique em "+ Nova Ficha" para iniciar sua lenda.</span></p>`;
        }
    }, (error) => {
        console.error("Erro no Firestore:", error);
        sheetContainer.innerHTML = `<p class="cinzel-font text-xl font-bold text-center text-red-800">Ocorreu um erro mágico ao carregar os dados.<br><span class="text-sm font-sans">${error.message}</span></p>`;
    });
};

/**
 * Renderiza o HTML da ficha (View Mode vs Edit Mode).
 */
const renderCharacterSheet = (character) => {
    if (!character) {
        return `<p class="cinzel-font text-2xl font-bold text-center">Selecione ou crie uma nova ficha.</p>`;
    }
    
    // Helper para renderizar campos
    const Field = (key, label, value, type = 'text', isAttribute = false) => {
        if (isEditing) {
            let modifier = Math.floor((value - 10) / 2);
            let attributeLabel = isAttribute ? ` (${modifier >= 0 ? '+' : ''}${modifier})` : '';
            return `
                <label class="text-xs uppercase font-bold text-yellow-900 block mb-1">${label}${attributeLabel}</label>
                <input id="edit-${key}" class="edit-input ${isAttribute ? 'text-3xl font-bold text-center w-full' : 'text-xl w-full'}" type="${type}" value="${value}" data-key="${key}">
            `;
        } else {
            if (isAttribute) {
                let modifier = Math.floor((value - 10) / 2);
                return `
                    <p class="text-xs uppercase font-bold text-yellow-900 opacity-80">${label}</p>
                    <p class="cinzel-font text-3xl font-bold text-gray-900">${value}</p>
                    <p class="text-lg font-bold text-gray-600 bg-white/30 rounded px-2 inline-block min-w-[40px]">${modifier >= 0 ? '+' : ''}${modifier}</p>
                `;
            } else {
                return `
                    <p class="text-xs uppercase font-bold text-yellow-900 opacity-80">${label}</p>
                    <p class="cinzel-font text-xl font-bold text-gray-900">${value}</p>
                `;
            }
        }
    };
    
    // Renderização das Perícias
    const skillsHtml = isEditing ? 
        character.skills.map((skill, index) => `
            <li class="flex gap-2 border-b border-gray-400/30 pb-2 mb-2 items-center">
                <input id="edit-skill-name-${index}" class="edit-input w-2/3 text-sm" type="text" value="${skill.name}" placeholder="Nome da Perícia">
                <input id="edit-skill-mod-${index}" class="edit-input w-1/3 text-center font-bold text-green-800" type="text" value="${skill.modifier}" placeholder="+0">
            </li>
        `).join('')
        :
        character.skills.map(skill => `
            <li class="flex justify-between border-b border-gray-400/30 pb-1 mb-1 last:border-0">
                <span class="font-medium text-gray-800">${skill.name}</span>
                <span class="font-bold text-green-800 font-cinzel">${skill.modifier}</span>
            </li>
        `).join('');

    // HTML Principal
    return `
        <div class="sheet-paper p-6 relative">
            ${isEditing ? `
                <div class="mb-6 text-center">
                    <label class="text-xs text-yellow-900 font-bold">NOME DO HERÓI</label>
                    <input id="edit-name" class="edit-input cinzel-font text-3xl font-bold mb-2 text-center w-full" type="text" value="${character.name}">
                    
                    <div class="flex justify-center gap-4 items-end mt-2">
                        <div class="w-20">
                            <label class="text-xs text-gray-600">Nível</label>
                            <input id="edit-level" class="edit-input text-center w-full font-bold" type="number" value="${character.level}">
                        </div>
                        <div class="w-1/3">
                            <label class="text-xs text-gray-600">Raça</label>
                            <input id="edit-race" class="edit-input text-center w-full" type="text" value="${character.race}">
                        </div>
                        <div class="w-1/3">
                            <label class="text-xs text-gray-600">Classe</label>
                            <input id="edit-class" class="edit-input text-center w-full" type="text" value="${character.class}">
                        </div>
                    </div>
                </div>
            ` : `
                <div class="text-center mb-6">
                    <h2 class="cinzel-font text-4xl font-bold text-gray-900 mb-1 tracking-wide">${character.name}</h2>
                    <div class="text-lg italic text-gray-700 font-serif border-t border-b border-gray-400/50 py-1 inline-block px-10">
                        Nível ${character.level} - ${character.race} ${character.class}
                    </div>
                </div>
            `}

            <div class="separator mb-6"></div>

            <div class="grid grid-cols-3 gap-4 mb-8 text-center">
                <div class="attribute-box p-3 rounded-lg shadow-sm">
                    ${Field('hp', 'PV (Vida)', character.hp, 'number')}
                </div>
                <div class="attribute-box p-3 rounded-lg shadow-sm">
                    ${Field('ac', 'CA (Defesa)', character.ac, 'number')}
                </div>
                <div class="attribute-box p-3 rounded-lg shadow-sm">
                    ${Field('bab', 'BBA (Ataque)', character.bab, 'text')}
                </div>
            </div>

            <div class="mb-8">
                <h3 class="section-title text-center mb-4">Atributos</h3>
                <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                    ${Object.entries(character.attributes).map(([attr, val]) => `
                        <div class="attribute-box p-2 rounded-md text-center relative group hover:bg-black/5 transition-colors">
                            ${Field(`attr-${attr}`, attr.toUpperCase(), val, 'number', true)}
                        </div>
                    `).join('')}
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div class="bg-white/30 p-4 rounded-lg border border-gray-300/50">
                    <h3 class="section-title mb-4">Perícias & Talentos</h3>
                    <ul class="space-y-1">
                        ${skillsHtml}
                    </ul>
                </div>

                <div class="flex flex-col gap-6">
                    <div class="bg-white/30 p-4 rounded-lg border border-gray-300/50 flex-grow">
                        <h3 class="section-title mb-2">Equipamento</h3>
                        ${isEditing ? `
                            <textarea id="edit-equipment" class="edit-textarea w-full h-32 bg-transparent" placeholder="Liste seus itens...">${character.equipment}</textarea>
                        ` : `
                            <p class="text-sm text-gray-800 whitespace-pre-line leading-relaxed">${character.equipment}</p>
                        `}
                    </div>

                    <div class="bg-white/30 p-4 rounded-lg border border-gray-300/50">
                        <h3 class="section-title mb-2">História</h3>
                        ${isEditing ? `
                            <textarea id="edit-description" class="edit-textarea w-full h-32 bg-transparent" placeholder="Conte sua lenda...">${character.description}</textarea>
                        ` : `
                            <p class="text-sm italic text-gray-700 whitespace-pre-line leading-relaxed font-serif">${character.description}</p>
                        `}
                    </div>
                </div>
            </div>
            
            ${isEditing ? `
                <div class="mt-8 pt-6 border-t-2 border-double border-gray-400 flex justify-between gap-4 items-center">
                    <button id="deleteBtn" class="delete-button text-white py-2 px-4 rounded shadow hover:bg-red-900 transition-colors text-sm font-bold uppercase tracking-wider" ${character.id ? '' : 'disabled'}>
                        <span class="mr-2">🗑️</span>Excluir
                    </button>
                    <button id="saveBtn" class="save-button text-white py-3 px-8 rounded shadow-lg hover:scale-105 transition-transform font-bold uppercase tracking-widest flex-grow max-w-md mx-auto text-lg">
                        <span id="save-text">Salvar Alterações</span>
                    </button>
                </div>
            ` : ''}
        </div>
    `;
};

/**
 * Coleta dados do form.
 */
const collectFormData = () => {
    const getVal = (id, def) => {
        const el = document.getElementById(id);
        return el ? el.value : def;
    };

    const data = {
        name: getVal('edit-name', 'Novo Personagem'),
        level: parseInt(getVal('edit-level', 1)),
        race: getVal('edit-race', 'Raça'),
        class: getVal('edit-class', 'Classe'),
        hp: parseInt(getVal('edit-hp', 10)),
        ac: parseInt(getVal('edit-ac', 10)),
        bab: getVal('edit-bab', '+0'),
        equipment: getVal('edit-equipment', ''),
        description: getVal('edit-description', ''),
        attributes: {},
        skills: []
    };

    ['str', 'dex', 'con', 'int', 'wis', 'cha'].forEach(attr => {
        data.attributes[attr] = parseInt(getVal(`edit-attr-${attr}`, 10));
    });

    for (let i = 0; i < 3; i++) {
        const name = getVal(`edit-skill-name-${i}`, '');
        const mod = getVal(`edit-skill-mod-${i}`, '+0');
        if (name) data.skills.push({ name, modifier: mod });
    }
    
    data.updatedAt = Date.now();
    data.userId = userId;

    return data;
};

// --- Funções de CRUD (Save, Delete, Add) mantidas iguais à lógica original ---

const saveCharacter = async () => {
    const saveButton = document.getElementById('saveBtn');
    const saveText = document.getElementById('save-text');
    if (!saveButton || saveButton.disabled) return;

    saveButton.disabled = true;
    saveText.textContent = 'Salvando...';
    
    const { doc, collection, setDoc } = window; // Firebase globals
    const character = characters[currentIndex];
    const data = collectFormData();
    
    const docId = character.id || doc(collection(db, `artifacts/${appId}/public/data/${CHARACTER_COLLECTION_PATH}`)).id;
    const docRef = doc(db, `artifacts/${appId}/public/data/${CHARACTER_COLLECTION_PATH}`, docId);

    try {
        await setDoc(docRef, data, { merge: true });
        isEditing = false;
        toggleEditBtn.textContent = 'Alternar Modo de Edição';
        updateSheetDisplay(true);
    } catch (error) {
        console.error("Erro ao salvar:", error);
        alert("Erro ao salvar. Verifique o console.");
    } finally {
        if(saveButton) saveButton.disabled = false;
        if(saveText) saveText.textContent = 'Salvar Ficha';
    }
};

const deleteCharacter = async () => {
    const character = characters[currentIndex];
    if (!character || !character.id) return;
    
    if (!window.confirm("Queimar este pergaminho para sempre? (Excluir)")) return;

    const { doc, deleteDoc } = window;
    try {
        const docRef = doc(db, `artifacts/${appId}/public/data/${CHARACTER_COLLECTION_PATH}`, character.id);
        await deleteDoc(docRef);
        isEditing = false;
        toggleEditBtn.textContent = 'Alternar Modo de Edição';
    } catch (error) {
        console.error("Erro ao excluir:", error);
    }
};

const addNewCharacter = () => {
    const newCharacter = {
        name: "Novo Aventureiro",
        race: "Humano",
        class: "Guerreiro",
        level: 1,
        hp: 10,
        ac: 10,
        bab: "+1",
        attributes: { str: 14, dex: 12, con: 14, int: 10, wis: 10, cha: 10 },
        skills: [{ name: "Atletismo", modifier: "+4" }, { name: "Intimidação", modifier: "+2" }, { name: "", modifier: "" }],
        equipment: "Espada Longa, Cota de Malha, Mochila de Aventureiro.",
        description: "Um bravo guerreiro iniciando sua jornada..."
    };
    
    characters.push(newCharacter);
    currentIndex = characters.length - 1;
    isEditing = true;
    toggleEditBtn.textContent = 'Cancelar Edição';
    updateSheetDisplay(true);
};

const updateSheetDisplay = (skipAnimation = false) => {
    const charCount = characters.length;
    if (charCount === 0) {
        if(prevBtn) prevBtn.disabled = true;
        if(nextBtn) nextBtn.disabled = true;
        return;
    }
    
    const transitionDuration = skipAnimation ? 0 : 300;

    // Classes Tailwind para transição de opacidade
    sheetContainer.classList.remove('opacity-100', 'translate-y-0');
    sheetContainer.classList.add('opacity-0', 'translate-y-4');

    setTimeout(() => {
        const character = characters[currentIndex];
        sheetContainer.innerHTML = renderCharacterSheet(character);
        
        // Retorna
        sheetContainer.classList.remove('opacity-0', 'translate-y-4');
        sheetContainer.classList.add('opacity-100', 'translate-y-0');

        if(prevBtn) prevBtn.disabled = currentIndex === 0;
        if(nextBtn) nextBtn.disabled = currentIndex === charCount - 1;
        
        if (isEditing) {
            document.getElementById('saveBtn')?.addEventListener('click', saveCharacter);
            document.getElementById('deleteBtn')?.addEventListener('click', deleteCharacter);
        }
    }, transitionDuration);
};

const nextCharacter = () => {
    if (currentIndex < characters.length - 1 && !isEditing) {
        currentIndex++;
        updateSheetDisplay();
    }
};

const prevCharacter = () => {
    if (currentIndex > 0 && !isEditing) {
        currentIndex--;
        updateSheetDisplay();
    }
};

const toggleEditMode = () => {
    if (characters.length === 0 && !isEditing) {
        addNewCharacter();
        return;
    }
    isEditing = !isEditing;
    toggleEditBtn.textContent = isEditing ? 'Cancelar Edição' : 'Alternar Modo de Edição';
    updateSheetDisplay(true);
};

const setupEventListeners = () => {
    if(prevBtn) prevBtn.addEventListener('click', prevCharacter);
    if(nextBtn) nextBtn.addEventListener('click', nextCharacter);
    if(toggleEditBtn) toggleEditBtn.addEventListener('click', toggleEditMode);
    if(addCharacterBtn) addCharacterBtn.addEventListener('click', addNewCharacter);
};