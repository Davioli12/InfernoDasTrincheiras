// =============================================================
// Inferno das Trincheiras — game.js
// =============================================================

const socket = io("https://davioli12.pythonanywhere.com", {
    transports: ["polling"],
    upgrade: false
});
socket.emit('update', { status: 'running' });

let currentRoom = null;
let myPlayerId = null;
let wasStarted = false;
let winnerLogged = false;
let devConsoleEnabled = false;

// Mapeamento de tipo de carta para cor de fundo do badge
const TYPE_COLORS = {
    attack: "#8B0000",
    heal: "#2d5a27",
    defense: "#1a3a5c",
    resource: "#8B6914",
    spy: "#4a1870",
    historical: "#6b4c1a",
};

// Rótulos legíveis por tipo
const TYPE_LABELS = {
    attack: "Ataque",
    heal: "Cura",
    defense: "Defesa",
    resource: "Recurso",
    spy: "Espionagem",
    historical: "Histórica",
};

// Símbolo por raridade
const RARITY_SYMBOLS = {
    Common: "◆",
    Rare: "◆◆",
    Epic: "◆◆◆",
    Legendary: "★",
};

const RARITY_COLORS = {
    Common: "#aaa",
    Rare: "#4a90d9",
    Epic: "#c084fc",
    Legendary: "#FFD700",
};


// ======================
// CRIAR SALA
// ======================

function createRoom() {
    const name = document.getElementById("name").value.trim();
    if (!name) { alert("Digite seu nome."); return; }

    const maxPlayers = parseInt(document.getElementById("max-players").value);
    socket.emit("create_room", { name, max_players: maxPlayers });
}

function startMatch() {
    socket.emit("start_game", { room: currentRoom });
}


// ======================
// ENTRAR SALA
// ======================

function joinRoom() {
    const name = document.getElementById("name").value.trim();
    const room = document.getElementById("room").value.trim();

    if (!name || !room) { alert("Preencha nome e sala."); return; }

    socket.emit("join_room_game", { room: room.toUpperCase(), name });
}


// ======================
// TROCAR TELA
// ======================

function showGameScreen() {
    document.getElementById("join-screen").style.display = "none";
    document.getElementById("game-screen").style.display = "block";
}

function setRoomCode(code) {
    document.getElementById("room-code").innerText = code;
}


// ======================
// SALA CRIADA
// ======================

socket.on("room_created", data => {
    currentRoom = data.room;
    myPlayerId = data.player_id;

    showGameScreen();
    setRoomCode(currentRoom);
    updateGame(data.game);
    addLog(`🏠 Sala criada: <strong>${currentRoom}</strong>`);
});


// ======================
// ENTROU NA SALA
// ======================

socket.on("room_joined", data => {
    currentRoom = data.room;
    myPlayerId = data.player_id;

    showGameScreen();
    setRoomCode(currentRoom);
    addLog(`🚪 Você entrou na sala <strong>${currentRoom}</strong>`);
});


// ======================
// LISTAR SALAS (LOBBY)
// ======================

function requestRoomList() {
    socket.emit("list_lobby_rooms");
}

socket.on("lobby_rooms", data => {
    const container = document.getElementById("room-list");
    if (!container) return;

    const rooms = Array.isArray(data.rooms) ? data.rooms : [];

    if (rooms.length === 0) {
        container.innerHTML = `<div class="no-rooms">Nenhuma sala disponível.</div>`;
        return;
    }

    const html = rooms.map(r => {
        return `
            <div class="room-item">
                <div class="room-id">${r.room}</div>
                <div class="room-count">${r.players}/${r.max_players}</div>
                <div class="room-actions"><button onclick="joinRoomByCode('${r.room}')">Entrar</button></div>
            </div>
        `;
    }).join("");

    container.innerHTML = html;
});

function joinRoomByCode(code) {
    document.getElementById("room").value = code;
    joinRoom();
}


// ======================
// UPDATE DA SALA
// ======================

socket.on("room_update", data => {
    updateGame(data);
});


// ======================
// ERRO
// ======================

socket.on("error_message", data => {
    console.log(data.message);
});

socket.on("dev_access", data => {
    devConsoleEnabled = Boolean(data.enabled);
    console.log("🛠️ Console de desenvolvedor ativado.", data.commands || []);
});

window.devCommand = function (command, payload = {}) {
    if (!devConsoleEnabled) {
        console.warn("Acesso de console negado.");
        return;
    }

    socket.emit("dev_command", {
        room: currentRoom,
        command,
        ...payload
    });
};

function renderDevConsole() {
    const el = document.getElementById("dev-console");
    if (!el) return;
    if (devConsoleEnabled) {
        el.style.display = "block";
    } else {
        el.style.display = "none";
    }

    const sendBtn = document.getElementById("dev-send-btn");
    const cmdSelect = document.getElementById("dev-command-select");
    const payloadInput = document.getElementById("dev-payload");

    if (sendBtn && !sendBtn._bound) {
        sendBtn.addEventListener("click", () => {
            const cmd = cmdSelect.value;
            let payload = {};
            try {
                const txt = (payloadInput.value || "").trim();
                payload = txt ? JSON.parse(txt) : {};
            } catch (e) {
                console.warn("Payload JSON inválido", e);
                alert("Payload JSON inválido. Corrija e tente novamente.");
                return;
            }

            window.devCommand(cmd, payload);
        });
        sendBtn._bound = true;
    }
}

// Atualiza visibilidade do console sempre que receber o evento
socket.on("dev_access", data => {
    devConsoleEnabled = Boolean(data.enabled);
    renderDevConsole();
});

// Tenta renderizar no load (caso já tenha sido recebido antes)
window.addEventListener("load", () => setTimeout(renderDevConsole, 100));


// ======================
// LOG DE EVENTO (servidor)
// ======================

socket.on("game_log", data => {
    addLog(data.message);
});

// ===============
// GAME INFO
// ===============
socket.on("game_info", data => {
    dev_game = data;
    console.log(data);
});



// ======================
// INTEL REVELADA
// ======================

socket.on("intel_revealed", data => {
    const lines = data.players.map(p => {
        const nomes = p.cards.map(c => c.name).join(", ");
        return `<strong>${p.player}</strong>: ${nomes}`;
    });

    addLog(`🔍 Inteligência revelada:<br>${lines.join("<br>")}`);

    // Mostra modal com as cartas inimigas
    mostrarIntelModal(data.players);
});


// ======================
// JOGADOR ELIMINADO
// ======================

socket.on("player_eliminated", data => {
    addLog(`💀 <strong>${data.name}</strong> foi eliminado!`);
});


// ======================
// UPDATE GERAL
// ======================

function updateGame(data) {
    renderPhaseSections(data);
    renderLobbyPlayers(data.players);
    renderHostName(data);
    renderTeams(data.players, data.current_player_id);
    renderResources(data.resources);
    renderGameInfo(data);
    renderHand(data);
    renderStartButton(data);
    renderWinner(data);
    renderTruceIndicator(data);

    if (!wasStarted && data.started) {
        addLog("⚔️ A partida começou!");
    }
    wasStarted = data.started;

    if (data.winner && !winnerLogged) {
        addLog(`🏆 Fim de jogo! Vencedor: <strong>${data.winner}</strong>`);
        winnerLogged = true;
    }

    if (!data.winner) winnerLogged = false;
}


// ======================
// FASES (lobby x jogo)
// ======================

function renderPhaseSections(data) {
    const lobby = document.getElementById("lobby-section");
    const resources = document.getElementById("resources-wrapper");
    const teams = document.getElementById("teams-wrapper");

    if (data.started) {
        lobby.style.display = "none";
        resources.style.display = "grid";
        teams.style.display = "grid";
    } else {
        lobby.style.display = "block";
        resources.style.display = "none";
        teams.style.display = "none";
    }
}


// ======================
// INDICADOR DE TRÉGUA
// ======================

function renderTruceIndicator(data) {
    let indicator = document.getElementById("truce-indicator");

    if (!indicator) {
        indicator = document.createElement("div");
        indicator.id = "truce-indicator";
        indicator.className = "truce-banner";
        document.getElementById("game-screen").prepend(indicator);
    }

    const truce = data.truce_rounds || 0;

    if (truce > 0 && data.started) {
        indicator.style.display = "block";
        indicator.innerHTML = `☮️ Trégua ativa — ${truce} rodada(s) restante(s). Ataques bloqueados.`;
    } else {
        indicator.style.display = "none";
    }
}


// ======================
// JOGADORES NO LOBBY
// ======================

function renderLobbyPlayers(players) {
    let html = "";

    players.forEach(player => {
        html += `
        <div class="lobby-player">
            ${player.name}${player.id === myPlayerId ? " (você)" : ""}
        </div>`;
    });

    document.getElementById("lobby-players").innerHTML =
        html || "<p>Nenhum jogador ainda.</p>";
}


// ======================
// NOME DO HOST
// ======================

function renderHostName(data) {
    const host = data.players.find(p => p.id === data.host_id);
    document.getElementById("host-name").innerText =
        host ? host.name : "------";
}


// ======================
// BOTÃO DE INICIAR
// ======================

function renderStartButton(data) {
    const btn = document.getElementById("start-game-btn");
    const isHost = data.host_id === myPlayerId;
    const canStart = isHost && !data.started && !data.winner;

    btn.style.display = canStart ? "block" : "none";
}


// ======================
// VENCEDOR
// ======================

function renderWinner(data) {
    const banner = document.getElementById("winner-banner");

    if (data.winner) {
        const me = data.players.find(p => p.id === myPlayerId);
        const myTeam = me ? me.team : null;
        const won = myTeam && myTeam === data.winner;
        const bonusWinners = Array.isArray(data.winner_bonus) ? data.winner_bonus : [];
        const bonusText = bonusWinners.length > 0
            ? ` (<strong>${bonusWinners.join(", ")}</strong> também ganhou)`
            : "";

        banner.style.display = "block";
        banner.classList.toggle("winner-banner-win", won);
        banner.classList.toggle("winner-banner-lose", !won);
        banner.innerHTML = `
            <div class="winner-banner-title">🏆 Vitória dos ${data.winner}${bonusText}!</div>
            <div class="winner-banner-subtitle">${won
                ? `🎉 Parabéns! Sua equipe (${myTeam}) venceu!`
                : `💪 Não foi dessa vez. Sua equipe (${myTeam || "sua equipe"}) perdeu, mas isso só te deixa mais forte.`}
            </div>
            <div class="winner-banner-message">${won
                ? "Sua estratégia foi valente e sua luta ajudou a conquistar a vitória. Prepare-se para a próxima rodada!"
                : "Use essa experiência para ajustar a próxima tática e voltar ainda mais preparado. Seu esforço já fez diferença."}
            </div>
        `;
    } else {
        banner.style.display = "none";
        banner.classList.remove("winner-banner-win", "winner-banner-lose");
        banner.innerHTML = "";
    }
}


// ======================
// RECURSOS
// ======================

function renderResources(resources) {
    renderTeamResources("resources-allies", resources["Aliados"]);
    renderTeamResources("resources-central", resources["Centrais"]);
}

function renderTeamResources(containerId, data) {
    const ICONS = { food: "🍞", ammo: "🔫", morale: "📢" };

    let html = "";

    Object.entries(data || {}).forEach(([k, v]) => {
        html += `
        <div class="resource-card">
            <span class="resource-icon">${ICONS[k] || "📦"}</span>
            <h4>${k}</h4>
            <h2>${v}</h2>
        </div>`;
    });

    document.getElementById(containerId).innerHTML = html;
}


// ======================
// TURNO / FASE
// ======================

function renderGameInfo(data) {
    const info = document.getElementById("turn-info");

    if (data.winner) {
        info.innerHTML = "Partida encerrada";
        return;
    }

    if (!data.started) {
        info.innerHTML = "Fase: Lobby";
        return;
    }

    const current = data.players.find(p => p.id === data.current_player_id);
    const isMyTurn = data.current_player_id === myPlayerId;
    const roundInfo = data.round_count !== undefined
        ? ` · Rodada ${data.round_count}`
        : "";

    info.innerHTML = `
        Vez de: <strong>${current ? current.name : "—"}</strong>${roundInfo}
        ${isMyTurn ? '<span class="your-turn-badge">SUA VEZ</span>' : ""}
    `;
}


// ======================
// CARTAS NA MÃO
// ======================

function renderHand(data) {
    const me = data.players.find(p => p.id === myPlayerId);
    const hand = me ? me.hand : [];
    const isMyTurn = data.started && data.current_player_id === myPlayerId;

    let html = "";

    hand.forEach(card => {
        const typeColor = TYPE_COLORS[card.type] || "#333";
        const typeLabel = TYPE_LABELS[card.type] || card.type;
        const raritySymbol = RARITY_SYMBOLS[card.rarity] || "◆";
        const rarityColor = RARITY_COLORS[card.rarity] || "#aaa";

        const canPlay = isMyTurn && data.started && !data.winner;
        const clickAttr = canPlay
            ? `onclick="playCard(${card.id})"`
            : "";

        const cardFile = card.file || slugify(card.name);
        const extension = "webp"; // "webp" ou "png", dependendo do formato das imagens

        console.log(`Rendering card: ${card.name}, canPlay: ${canPlay}`);

        html += `
        <div class="card ${canPlay ? "" : "card-disabled"}" ${clickAttr}>

            <!-- Cabeçalho: tipo + raridade -->
            <div class="card-header-row">
                <span class="card-type-badge" style="background:${typeColor}">
                    ${typeLabel}
                </span>
                <span class="card-rarity" style="color:${rarityColor}" title="${card.rarity || ""}">
                    ${raritySymbol}
                </span>
            </div>

            <!-- Nome -->
            <div class="card-title">${card.name}</div>

            <!-- Imagem / ícone -->
            <div class="card-thumb" onclick="event.stopPropagation(); abrirCarta('${cardFile}')">
                <img
                    src="/static/cards/img/${cardFile}.${extension}"
                    alt="${card.name}"
                    onerror="this.style.display='none'; this.nextElementSibling.style.display='flex'"
                >
                <span class="card-thumb-fallback" style="display:none">🃏</span>

                <!-- Botão de abrir carta (desativado) -->
                <!-- <span class="card-thumb-hint">👁 ver</span> -->
            </div>

            <!-- Descrição -->
            <div class="card-description">${card.desc}</div>

            <!-- Botão de jogar -->
            ${canPlay ? `
            <button class="card-play-btn" onclick="playCard(${card.id})">
                Jogar
            </button>` : ""}

        </div>`;
    });

    document.getElementById("hand").innerHTML =
        html || "<p class='no-cards'>Sem cartas na mão.</p>";
}

/**
 * Converte o nome da carta em slug de arquivo.
 * Ex: "Médico de Campo" → "medico_campo"
 */
function slugify(name) {
    return name
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")   // remove acentos
        .replace(/[^a-z0-9]+/g, "_")        // espaços/pontos → _
        .replace(/^_+|_+$/g, "");           // trim underscores
}


// ======================
// JOGAR CARTA
// ======================

function playCard(cardId) {
    if (!currentRoom) return;

    socket.emit("play_card", {
        room: currentRoom,
        card_id: cardId
    });
}


// ======================
// TIMES
// ======================

function renderTeams(players, currentPlayerId) {
    let allies = "";
    let central = "";

    players.forEach(player => {
        const hpPercent = Math.max(0, (player.hp / player.max_hp) * 100);
        const isTurn = player.id === currentPlayerId;
        const isMe = player.id === myPlayerId;

        // Cor da barra de vida
        const hpColor = hpPercent > 60 ? "#4CAF50"
            : hpPercent > 30 ? "#FFA500"
                : "#e74c3c";

        const html = `
        <div class="player-card ${isTurn ? "active-turn" : ""} ${player.alive ? "" : "player-dead"}">

            <div class="player-header">
                <h3>${player.name}${isMe ? " <span class='you-tag'>(você)</span>" : ""}</h3>
                ${player.class ? `<span class="class-tag">${player.class}</span>` : ""}
            </div>

            <p>Vida: <strong>${player.hp}</strong> / ${player.max_hp}</p>

            <div class="hp-bar">
                <div class="hp-fill" style="width:${hpPercent}%; background:${hpColor}"></div>
            </div>

            <p class="shield-count">
                🛡️ Escudo: <strong>${player.shield ?? 0}</strong>
            </p>

            <p class="hand-count">
                🃏 Cartas: ${player.hand_count}
            </p>

            ${!player.alive ? '<p class="eliminated-tag">💀 Eliminado</p>' : ""}

        </div>`;

        if (player.team === "Aliados") allies += html;
        else if (player.team === "Centrais") central += html;
    });

    document.getElementById("allies").innerHTML = allies || "<p>Nenhum jogador.</p>";
    document.getElementById("central").innerHTML = central || "<p>Nenhum jogador.</p>";
}


// ======================
// LOG
// ======================

function addLog(message) {
    const log = document.getElementById("log");

    const item = document.createElement("div");
    item.className = "log-item";
    item.innerHTML = message;

    log.appendChild(item);
    log.scrollTop = log.scrollHeight;
}


// ======================
// ABRIR CARTA (OVERLAY)
// ======================

async function abrirCarta(slug) {

    const overlay = document.getElementById("card-overlay");

    overlay.classList.add("active");

    overlay.innerHTML = `
        <div class="card-overlay-loading">
            Carregando carta...
        </div>
    `;

    try {

        const response = await fetch(`/static/cards/${slug}.html`);

        if (!response.ok)
            throw new Error();

        const html = await response.text();

        const parser = new DOMParser();

        const doc = parser.parseFromString(
            html,
            "text/html"
        );

        overlay.innerHTML = `

            <div class="card-overlay-content">

                <button
                    class="card-overlay-close"
                    onclick="fecharCarta()">

                    ✕

                </button>

                ${doc.body.innerHTML}

            </div>

        `;

        doc.querySelectorAll("style").forEach(style => {

            overlay.appendChild(style.cloneNode(true));

        });

        doc.querySelectorAll("script").forEach(script => {

            const s = document.createElement("script");

            if (script.src) {

                s.src = script.src;

            } else {

                s.textContent = script.textContent;

            }

            overlay.appendChild(s);

        });

    } catch (e) {

        overlay.innerHTML = `

            <div class="card-overlay-content">

                <h2 style="color:white">

                    Carta não encontrada

                </h2>

                <button
                    class="card-overlay-close"
                    onclick="fecharCarta()">

                    ✕

                </button>

            </div>

        `;

    }

}

// ======================
// MODAL DE INTEL
// Exibe as cartas reveladas pelo Avião / Código Decifrado
// ======================

function mostrarIntelModal(players) {
    let html = `
    <div class="intel-modal">
        <h2>🔍 Cartas Inimigas Reveladas</h2>`;

    players.forEach(p => {
        html += `<h3>${p.player}</h3><div class="intel-cards">`;

        p.cards.forEach(card => {
            const typeColor = TYPE_COLORS[card.type] || "#333";
            html += `
            <div class="intel-card">
                <span class="card-type-badge" style="background:${typeColor}">
                    ${TYPE_LABELS[card.type] || card.type}
                </span>
                <strong>${card.name}</strong>
                <p>${card.desc}</p>
            </div>`;
        });

        html += `</div>`;
    });

    html += `
        <button onclick="fecharIntelModal()">Fechar</button>
    </div>`;

    // Usa o mesmo overlay de carta
    const overlay = document.getElementById("card-overlay");
    overlay.innerHTML = html;
    overlay.style.display = "flex";
}

function fecharIntelModal() {
    fecharCarta();
}

function imageError(img) {

    const placeholder = document.createElement("div");

    placeholder.className = "img-placeholder";

    placeholder.innerHTML = `
        <span>${img.alt}</span>
    `;

    img.replaceWith(placeholder);

}

// ======================
// PERFIS (localStorage)
// ======================

function loadProfiles() {
    try {
        const raw = localStorage.getItem('idt_profiles') || '[]';
        const profiles = JSON.parse(raw);

        const select = document.getElementById('profile-select');
        if (!select) return;

        // clear existing options
        select.innerHTML = '';

        const defaultOpt = document.createElement('option');
        defaultOpt.value = '';
        defaultOpt.textContent = 'Escolher perfil';
        select.appendChild(defaultOpt);

        profiles.forEach(name => {
            const opt = document.createElement('option');
            opt.value = name;
            opt.textContent = name;
            select.appendChild(opt);
        });

    } catch (e) {
        console.error('Erro ao carregar perfis', e);
    }
}

function saveProfileFromInput() {
    const input = document.getElementById('name');
    if (!input) return;

    const name = input.value.trim();
    if (!name) { alert('Digite um nome antes de salvar o perfil.'); return; }

    try {
        const raw = localStorage.getItem('idt_profiles') || '[]';
        const profiles = JSON.parse(raw);

        if (!profiles.includes(name)) {
            profiles.push(name);
            localStorage.setItem('idt_profiles', JSON.stringify(profiles));
        }

        loadProfiles();

        // select the newly saved profile
        const select = document.getElementById('profile-select');
        if (select) select.value = name;

        addLog(`💾 Perfil salvo: <strong>${name}</strong>`);
    } catch (e) {
        console.error('Erro ao salvar perfil', e);
        alert('Não foi possível salvar o perfil. Veja o console.');
    }
}

function selectProfile(value) {
    const input = document.getElementById('name');
    if (!input) return;
    input.value = value || '';
}


function closeCredits() {
    const credits = document.getElementById('credits');
    const containers = document.getElementsByClassName('container');

    // Ensure both elements exist
    if (credits && containers.length > 0) {
        credits.style.display = 'none';           // Hide credits
        containers[0].style.display = 'block';    // Show first container
    } else {
        try {
            if (!credits) throw new Error("Credits element not found.");
            if (containers.length === 0) throw new Error("Container elements not found.");
        } catch (error) {
            console.error(error.message);
            alert("Erro ao fechar créditos. Veja o console para mais detalhes.");
        }
        console.warn("Credits element or container not found.");
    }
}

// Popula o select na inicialização
document.addEventListener('DOMContentLoaded', loadProfiles);