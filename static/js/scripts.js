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
 * Ela recebe as instâncias do Firebase e os IDs necessários.
 * * @param {object} firestoreDb - Instância do Firestore.
 * @param {string} authUserId - ID do usuário autenticado.
 * @param {string} currentAppId - ID da aplicação.
 */
window.initApp = (firestoreDb, authUserId, currentAppId) => {
    // Importa as funções do Firestore globalmente (disponíveis via window no index.html)
    db = firestoreDb;
    userId = authUserId;
    appId = currentAppId;

    // Exibe os botões de controle após a autenticação
    toggleEditBtn.classList.remove('hidden');
    addCharacterBtn.classList.remove('hidden');
    toggleEditBtn.disabled = false;
    addCharacterBtn.disabled = false;

    setupFirestoreListener();
    setupEventListeners();
};

/**
 * Configura o listener em tempo real para as fichas de personagem no Firestore.
 */
const setupFirestoreListener = () => {
    // Certifica-se de que as dependências do Firestore estão disponíveis
    if (typeof collection === 'undefined' || !db || !appId) return;

    // Caminho da coleção pública: /artifacts/{appId}/public/data/ragnarok_characters
    const characterRef = collection(db, `artifacts/${appId}/public/data/${CHARACTER_COLLECTION_PATH}`);
    const q = query(characterRef);

    // onSnapshot para ouvir as mudanças em tempo real
    onSnapshot(q, (snapshot) => {
        const fetchedCharacters = [];
        snapshot.forEach((doc) => {
            // Adiciona o ID do documento ao objeto da ficha
            fetchedCharacters.push({ id: doc.id, ...doc.data() });
        });
        
        characters = fetchedCharacters;
        
        // Garante que o índice atual seja válido após a atualização
        if (currentIndex >= characters.length && characters.length > 0) {
            currentIndex = characters.length - 1;
        } else if (characters.length === 0) {
            currentIndex = 0;
        }

        updateSheetDisplay(true); // Força a atualização da exibição sem animação
        console.log(`Fichas carregadas: ${characters.length}`);

        // Se não houver fichas, exibe uma mensagem
        if (characters.length === 0) {
            sheetContainer.innerHTML = `<p class="cinzel-font text-2xl font-bold text-center">Nenhuma ficha encontrada. Clique em "+ Nova Ficha" para começar!</p>`;
        }
    }, (error) => {
        console.error("Erro ao ouvir o Firestore:", error);
        sheetContainer.innerHTML = `<p class="cinzel-font text-2xl font-bold text-center text-red-700">Erro ao carregar dados: ${error.message}</p>`;
    });
};

/**
 * Gera o HTML da ficha de personagem atual, alternando entre modo de visualização e edição.
 * @param {object} character - O objeto do personagem.
 * @returns {string} HTML renderizado.
 */
const renderCharacterSheet = (character) => {
    if (!character) {
        return `<p class="cinzel-font text-2xl font-bold text-center">Selecione ou crie uma nova ficha.</p>`;
    }
    
    // Helper para gerar campos de entrada vs texto
    const Field = (key, label, value, type = 'text', isAttribute = false) => {
        if (isEditing) {
            // Calcula o modificador D&D 3.5 e formata a label
            let modifier = Math.floor((value - 10) / 2);
            let attributeLabel = isAttribute ? ` (${modifier >= 0 ? '+' : ''}${modifier})` : '';
            return `
                <label class="text-xs uppercase font-bold text-yellow-700 block">${label}${attributeLabel}</label>
                <input id="edit-${key}" class="edit-input ${isAttribute ? 'text-3xl font-bold text-center' : 'text-xl'}" type="${type}" value="${value}" data-key="${key}">
            `;
        } else {
            if (isAttribute) {
                let modifier = Math.floor((value - 10) / 2);
                return `
                    <p class="text-xs uppercase font-bold text-yellow-700">${label}</p>
                    <p class="cinzel-font text-3xl font-bold">${value}</p>
                    <p class="text-lg font-medium text-gray-600">${modifier >= 0 ? '+' : ''}${modifier}</p>
                `;
            } else {
                return `<p class="text-sm">${value}</p>`;
            }
        }
    };
    
    // Monta a seção de Perícias (assumindo 3 para edição simples)
    const skillsHtml = isEditing ? 
        character.skills.map((skill, index) => `
            <li class="flex gap-2 border-b border-gray-300 pb-1 items-center">
                <input id="edit-skill-name-${index}" class="edit-input w-2/3" type="text" value="${skill.name}" placeholder="Nome da Perícia">
                <input id="edit-skill-mod-${index}" class="edit-input w-1/3 text-center font-bold text-green-700" type="text" value="${skill.modifier}" placeholder="+X">
            </li>
        `).join('')
        :
        character.skills.map(skill => `
            <li class="flex justify-between border-b border-gray-300 pb-1">
                <span class="font-medium">${skill.name}</span>
                <span class="font-bold text-green-700">${skill.modifier}</span>
            </li>
        `).join('');

    // HTML principal da Ficha
    return `
        ${isEditing ? `
            <!-- Campos de Edição do Topo -->
            <input id="edit-name" class="edit-input cinzel-font text-3xl font-bold mb-1 text-center" type="text" value="${character.name}">
            <div class="text-center text-lg italic mb-4">
                Nível <input id="edit-level" class="edit-input w-12 inline text-center" type="number" value="${character.level}"> - 
                <input id="edit-race" class="edit-input w-1/4 inline text-center" type="text" value="${character.race}"> 
                <input id="edit-class" class="edit-input w-1/4 inline text-center" type="text" value="${character.class}">
            </div>
        ` : `
            <!-- Modo de Visualização do Topo -->
            <h2 class="cinzel-font text-3xl font-bold mb-1 text-center">${character.name}</h2>
            <div class="text-center text-lg italic mb-4">Nível ${character.level} - ${character.race} ${character.class}</div>
        `}

        <div class="separator mb-4"></div>

        <!-- Seção de Estatísticas Chave -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6 text-center">
            <div class="attribute-box p-3 rounded-md">
                ${Field('hp', 'Pontos de Vida (PV)', character.hp, 'number')}
            </div>
            <div class="attribute-box p-3 rounded-md">
                ${Field('ac', 'Classe de Armadura (CA)', character.ac, 'number')}
            </div>
            <div class="attribute-box p-3 rounded-md">
                ${Field('bab', 'Bônus Base de Ataque (BBA)', character.bab, 'text')}
            </div>
        </div>

        <!-- Seção de Atributos -->
        <h3 class="cinzel-font text-xl font-semibold mb-3 text-center border-b-2 border-yellow-700 pb-1 text-yellow-700">Atributos (D&D 3.5)</h3>
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
            ${Object.entries(character.attributes).map(([attr, val]) => `
                <div class="attribute-box p-2 rounded-md text-center">
                    ${Field(`attr-${attr}`, attr.toUpperCase(), val, 'number', true)}
                </div>
            `).join('')}
        </div>

        <!-- Seção de Perícias e Equipamento -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
                <h3 class="cinzel-font text-xl font-semibold mb-3 text-yellow-700 border-b border-yellow-700 pb-1">Perícias Chave</h3>
                <ul class="space-y-2">
                    ${skillsHtml}
                </ul>
            </div>
            <div>
                <h3 class="cinzel-font text-xl font-semibold mb-3 text-yellow-700 border-b border-yellow-700 pb-1">Equipamento</h3>
                ${isEditing ? `
                    <textarea id="edit-equipment" class="edit-textarea">${character.equipment}</textarea>
                ` : `
                    <p class="text-sm">${character.equipment}</p>
                `}
                
                <h3 class="cinzel-font text-xl font-semibold mt-4 mb-3 text-yellow-700 border-b border-yellow-700 pb-1">História</h3>
                ${isEditing ? `
                    <textarea id="edit-description" class="edit-textarea">${character.description}</textarea>
                ` : `
                    <p class="text-sm italic">${character.description}</p>
                `}
            </div>
        </div>
        
        <!-- Botões de Ação na Edição -->
        ${isEditing ? `
            <div class="mt-6 flex justify-between gap-4">
                <button id="saveBtn" class="save-button text-white py-2 px-6 rounded-lg shadow-xl font-bold flex-grow">
                    <span id="save-text">Salvar Ficha</span>
                </button>
                <button id="deleteBtn" class="delete-button text-white py-2 px-6 rounded-lg shadow-xl font-bold" ${character.id ? '' : 'disabled'}>
                    Excluir Ficha
                </button>
            </div>
        ` : ''}
    `;
};

/**
 * Coleta os dados dos campos de input no modo de edição.
 * @returns {object} O objeto da ficha com os dados atualizados.
 */
const collectFormData = () => {
    const data = {
        name: document.getElementById('edit-name')?.value || 'Novo Personagem',
        level: parseInt(document.getElementById('edit-level')?.value) || 1,
        race: document.getElementById('edit-race')?.value || 'Raça',
        class: document.getElementById('edit-class')?.value || 'Classe',
        hp: parseInt(document.getElementById('edit-hp')?.value) || 1,
        ac: parseInt(document.getElementById('edit-ac')?.value) || 10,
        bab: document.getElementById('edit-bab')?.value || '+0',
        equipment: document.getElementById('edit-equipment')?.value || '',
        description: document.getElementById('edit-description')?.value || '',
        attributes: {},
        skills: []
    };

    // Coletar atributos
    ['str', 'dex', 'con', 'int', 'wis', 'cha'].forEach(attr => {
        data.attributes[attr] = parseInt(document.getElementById(`edit-attr-${attr}`)?.value) || 10;
    });

    // Coletar perícias (assumindo 3 para simplicidade)
    for (let i = 0; i < 3; i++) {
        const nameEl = document.getElementById(`edit-skill-name-${i}`);
        const modEl = document.getElementById(`edit-skill-mod-${i}`);
        if (nameEl && nameEl.value) {
            data.skills.push({ name: nameEl.value, modifier: modEl?.value || '+0' });
        }
    }
    
    // Adiciona o timestamp para ajudar na ordenação
    data.updatedAt = Date.now();
    data.userId = userId;

    return data;
};

/**
 * Salva a ficha atual no Firestore (cria ou atualiza).
 */
const saveCharacter = async () => {
    const saveButton = document.getElementById('saveBtn');
    const saveText = document.getElementById('save-text');
    if (!saveButton || saveButton.disabled) return;

    saveButton.disabled = true;
    saveText.textContent = 'Salvando...';
    
    const character = characters[currentIndex];
    const data = collectFormData();
    
    // Se a ficha não tem ID, gera um novo caminho de documento
    const docId = character.id || doc(collection(db, `artifacts/${appId}/public/data/${CHARACTER_COLLECTION_PATH}`)).id;
    const docRef = doc(db, `artifacts/${appId}/public/data/${CHARACTER_COLLECTION_PATH}`, docId);

    try {
        await setDoc(docRef, data, { merge: true }); // setDoc com merge para criar ou atualizar
        console.log("Ficha salva com sucesso:", docId);
        
        // Desativa o modo de edição após salvar
        isEditing = false;
        toggleEditBtn.textContent = 'Alternar Modo de Edição';
        updateSheetDisplay(true);

    } catch (error) {
        console.error("Erro ao salvar a ficha:", error);
        // Não usa alert(), apenas loga o erro no console
        console.error("Erro ao salvar: Verifique as regras de segurança do Firestore ou a conexão.");
    } finally {
        saveButton.disabled = false;
        saveText.textContent = 'Salvar Ficha';
    }
};

/**
 * Exclui a ficha atual do Firestore.
 */
const deleteCharacter = async () => {
    const character = characters[currentIndex];
    if (!character || !character.id) {
        console.warn("Não é possível excluir: Ficha sem ID ou inexistente.");
        return;
    }
    
    // O ideal seria usar um modal customizado, mas aqui usaremos um log de aviso
    if (!window.confirm("Tem certeza que deseja excluir esta ficha permanentemente? (Use um modal customizado em produção!)")) {
        return;
    }

    try {
        const docRef = doc(db, `artifacts/${appId}/public/data/${CHARACTER_COLLECTION_PATH}`, character.id);
        await deleteDoc(docRef);
        console.log("Ficha excluída com sucesso:", character.id);
        
        // Desativa o modo de edição após a exclusão
        isEditing = false;
        toggleEditBtn.textContent = 'Alternar Modo de Edição';

    } catch (error) {
        console.error("Erro ao excluir a ficha:", error);
        console.error("Erro ao excluir: Verifique as regras de segurança do Firestore.");
    }
};

/**
 * Cria um novo objeto de ficha vazia (modelo) e entra no modo de edição.
 */
const addNewCharacter = () => {
    // Cria um modelo básico com um ID temporário para edição local
    const newCharacter = {
        name: "Novo Herói sem Nome",
        race: "Humano",
        class: "Aventureiro",
        level: 1,
        hp: 10,
        ac: 10,
        bab: "+0",
        attributes: { str: 10, dex: 10, con: 10, int: 10, wis: 10, cha: 10 },
        skills: [{ name: "Perícia 1", modifier: "+0" }, { name: "Perícia 2", modifier: "+0" }, { name: "Perícia 3", modifier: "+0" }],
        equipment: "Roupas e 1d6 de ouro.",
        description: "Uma nova alma pronta para o destino de Ragnarok."
        // Sem 'id' para forçar a criação de um novo documento no save
    };
    
    characters.push(newCharacter);
    currentIndex = characters.length - 1;
    isEditing = true;
    toggleEditBtn.textContent = 'Sair do Modo de Edição';
    updateSheetDisplay(true);
};


/**
 * Atualiza a exibição da ficha com base no índice atual, aplicando animação de transição.
 * @param {boolean} skipAnimation - Pula a animação se for uma atualização de dados (onSnapshot).
 */
const updateSheetDisplay = (skipAnimation = false) => {
    const charCount = characters.length;
    
    if (charCount === 0) {
        prevBtn.disabled = true;
        nextBtn.disabled = true;
        return;
    }

    // Importa doc e collection do escopo global se necessário (para listeners)
    const { doc, collection } = window;
    
    const transitionDuration = skipAnimation ? 0 : 500;

    // 1. Inicia o efeito de saída (opacidade 0, move para baixo)
    sheetContainer.classList.add('opacity-0', 'translate-y-4');

    setTimeout(() => {
        const character = characters[currentIndex];
        sheetContainer.innerHTML = renderCharacterSheet(character);
        
        // 3. Inicia o efeito de entrada (opacidade 1, retorna à posição)
        sheetContainer.classList.remove('opacity-0', 'translate-y-4');

        // 4. Atualiza o estado dos botões de navegação
        prevBtn.disabled = currentIndex === 0;
        nextBtn.disabled = currentIndex === charCount - 1;
        
        // 5. Adiciona listeners específicos para o modo de edição
        if (isEditing) {
            document.getElementById('saveBtn')?.addEventListener('click', saveCharacter);
            document.getElementById('deleteBtn')?.addEventListener('click', deleteCharacter);
        }
    }, transitionDuration);
};

/**
 * Avança para o próximo personagem no carrossel.
 */
const nextCharacter = () => {
    if (currentIndex < characters.length - 1 && !isEditing) {
        currentIndex++;
        updateSheetDisplay();
    } else if (isEditing) {
        console.warn("Saia do modo de edição para navegar.");
    }
};

/**
 * Retorna ao personagem anterior no carrossel.
 */
const prevCharacter = () => {
    if (currentIndex > 0 && !isEditing) {
        currentIndex--;
        updateSheetDisplay();
    } else if (isEditing) {
        console.warn("Saia do modo de edição para navegar.");
    }
};

/**
 * Alterna entre o modo de visualização e edição.
 */
const toggleEditMode = () => {
    if (characters.length === 0 && !isEditing) {
         // Se não há fichas, o botão de edição se comporta como "Adicionar nova"
         addNewCharacter();
         return;
    }
    
    isEditing = !isEditing;
    toggleEditBtn.textContent = isEditing ? 'Sair do Modo de Edição' : 'Alternar Modo de Edição';
    updateSheetDisplay(true); // Não usa animação ao alternar modos
};

/**
 * Configura os listeners de eventos.
 */
const setupEventListeners = () => {
    prevBtn.addEventListener('click', prevCharacter);
    nextBtn.addEventListener('click', nextCharacter);
    toggleEditBtn.addEventListener('click', toggleEditMode);
    addCharacterBtn.addEventListener('click', addNewCharacter);
};

// Observação: A inicialização da aplicação (initApp) é chamada pelo index.html após o processo de autenticação