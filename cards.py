import random

# =============================================================
# BARALHO OFICIAL — Inferno das Trincheiras
# Atualizado para incluir todas as 49 cartas do jogo.
#
# Efeitos suportados pelo servidor:
#   attack        → damage_single (1 inimigo aleatório)
#   aoe           → dano em todos os inimigos vivos
#   heal_self     → cura o jogador atual
#   shield_self   → escudo no jogador atual
#   shield_team   → escudo em todos da equipe
#   steal_resource→ rouba recurso do inimigo
#   resource      → ganha recurso para a equipe
#   reveal_intel  → revela cartas inimigas
#   truce         → pausa ataques por N rodadas
#   damage_single → ataque focado num inimigo
# =============================================================

CARDS = [

    # =========================================================
    # ATAQUE
    # =========================================================

    {
        "id": 1,
        "name": "Bombardeio",
        "file": "bombardeio",
        "type": "attack",
        "effect": "aoe",
        "damage": 2,
        "rarity": "Rare",
        "desc": "Chuva de projéteis devasta a linha inimiga. Causa 2 de dano a todos os inimigos.",
    },
    {
        "id": 2,
        "name": "Metralhadora",
        "file": "metralhadora",
        "type": "attack",
        "effect": "damage_single",
        "damage": 2,
        "rarity": "Common",
        "desc": "Causa 2 de dano a um inimigo aleatório.",
    },
    {
        "id": 3,
        "name": "Ataque de Infantaria",
        "file": "ataque_infantaria",
        "type": "attack",
        "effect": "damage_single",
        "damage": 4,
        "rarity": "Common",
        "desc": "Causa 4 de dano a um inimigo aleatório.",
    },
    {
        "id": 4,
        "name": "Granada",
        "file": "granada",
        "type": "attack",
        "effect": "aoe",
        "damage": 1,
        "rarity": "Common",
        "desc": "Arremesso certeiro. Causa 1 de dano a todos os inimigos.",
    },
    {
        "id": 5,
        "name": "Atirador de Elite",
        "file": "sniper",
        "type": "attack",
        "effect": "damage_single",
        "damage": 5,
        "rarity": "Rare",
        "desc": "Precisão letal. Causa 5 de dano a um inimigo escolhido.",
    },
    {
        "id": 6,
        "name": "Carga de Baioneta",
        "file": "carga_de_baioneta",
        "type": "attack",
        "effect": "damage_single",
        "damage": 3,
        "rarity": "Common",
        "desc": "Combate corpo a corpo. Causa 3 de dano a um inimigo.",
    },
    {
        "id": 7,
        "name": "Morteiro",
        "file": "morteiro",
        "type": "attack",
        "effect": "aoe",
        "damage": 2,
        "rarity": "Rare",
        "desc": "Projéteis curvos. Causa 2 de dano em área aos inimigos.",
    },
    {
        "id": 8,
        "name": "Artilharia Pesada",
        "file": "artilharia_pesada",
        "type": "attack",
        "effect": "damage_single",
        "damage": 6,
        "rarity": "Epic",
        "desc": "Canhões de longo alcance. Causa 6 de dano massivo a um inimigo.",
    },
    {
        "id": 9,
        "name": "Lança-Chamas",
        "file": "lanca_chamas",
        "type": "attack",
        "effect": "aoe",
        "damage": 3,
        "rarity": "Epic",
        "desc": "O fogo não perdoa. Causa 3 de dano a todos os inimigos.",
    },
    {
        "id": 10,
        "name": "Rajada de Rifle",
        "file": "rajada_rifle",
        "type": "attack",
        "effect": "damage_single",
        "damage": 1,
        "rarity": "Common",
        "desc": "Rápido e eficiente. Causa 1 de dano a um inimigo.",
    },
    {
        "id": 11,
        "name": "Carga de Cavalaria",
        "file": "carga_cavalaria",
        "type": "attack",
        "effect": "damage_single",
        "damage": 4,
        "rarity": "Rare",
        "desc": "A última grande carga. Causa 4 de dano e dá 1 de escudo ao jogador.",
    },
    {
        "id": 12,
        "name": "Canhão Ferroviário",
        "file": "canhao_ferroviario",
        "type": "attack",
        "effect": "aoe",
        "damage": 4,
        "rarity": "Legendary",
        "desc": "Destruição em escala industrial. Causa 4 de dano a TODOS os inimigos.",
    },
    {
        "id": 13,
        "name": "Ataque Noturno",
        "file": "ataque_noturno",
        "type": "attack",
        "effect": "damage_single",
        "damage": 3,
        "rarity": "Rare",
        "desc": "Sob a cobertura das trevas. Causa 3 de dano ignorando 1 de escudo.",
    },
    {
        "id": 14,
        "name": "Explosivos",
        "file": "explosivos",
        "type": "attack",
        "effect": "aoe",
        "damage": 3,
        "rarity": "Epic",
        "desc": "TNT estratégico. Causa 3 de dano em área a todos os inimigos.",
    },
    {
        "id": 15,
        "name": "Ofensiva Final",
        "file": "ofensiva_final",
        "type": "attack",
        "effect": "aoe",
        "damage": 5,
        "rarity": "Legendary",
        "desc": "O grande assalto. Causa 5 de dano a todos os inimigos. Tudo ou nada.",
    },

    # =========================================================
    # CURA
    # =========================================================

    {
        "id": 16,
        "name": "Médico de Campo",
        "file": "medico_campo",
        "type": "heal",
        "effect": "heal_self",
        "heal": 2,
        "rarity": "Common",
        "desc": "Recupera 2 de vida.",
    },
    {
        "id": 17,
        "name": "Hospital Militar",
        "file": "hospital_militar",
        "type": "heal",
        "effect": "heal_self",
        "heal": 4,
        "cost": {"food": 2},
        "rarity": "Rare",
        "desc": "Recupera 4 de vida em troca de 2 de comida.",
    },
    {
        "id": 18,
        "name": "Kit Médico",
        "file": "kit_medico",
        "type": "heal",
        "effect": "heal_self",
        "heal": 2,
        "rarity": "Common",
        "desc": "Morfina e curativos. Recupera 2 de vida e remove 1 efeito negativo.",
    },
    {
        "id": 19,
        "name": "Enfermeira Voluntária",
        "file": "enfermeira_voluntaria",
        "type": "heal",
        "effect": "heal_self",
        "heal": 3,
        "rarity": "Rare",
        "desc": "Dedicação sem fronteiras. Recupera 3 de vida.",
    },
    {
        "id": 20,
        "name": "Descanso na Retaguarda",
        "file": "descanso_retaguarda",
        "type": "heal",
        "effect": "heal_self",
        "heal": 3,
        "rarity": "Common",
        "desc": "Dias longe do front. Recupera 3 de vida.",
    },
    {
        "id": 21,
        "name": "Rações Extras",
        "file": "racoes_extras",
        "type": "heal",
        "effect": "heal_self",
        "heal": 1,
        "rarity": "Common",
        "desc": "Alimento é moral. Recupera 1 de vida.",
    },
    {
        "id": 22,
        "name": "Evacuação",
        "file": "evacuacao",
        "type": "heal",
        "effect": "heal_self",
        "heal": 3,
        "rarity": "Rare",
        "desc": "Retirada estratégica. Recupera 3 de vida.",
    },
    {
        "id": 23,
        "name": "Cirurgia de Emergência",
        "file": "cirurgia_emergencia",
        "type": "heal",
        "effect": "heal_self",
        "heal": 6,
        "rarity": "Epic",
        "desc": "Operação desesperada. Recupera 6 de vida instantaneamente.",
    },

    # =========================================================
    # DEFESA
    # =========================================================

    {
        "id": 24,
        "name": "Reforçar Trincheira",
        "file": "reforcar_trincheira",
        "type": "defense",
        "effect": "shield_self",
        "shield": 2,
        "rarity": "Common",
        "desc": "Madeira e lama. Ganha 2 de escudo.",
    },
    {
        "id": 25,
        "name": "Sacos de Areia",
        "file": "sacos_areia",
        "type": "defense",
        "effect": "shield_self",
        "shield": 2,
        "rarity": "Common",
        "desc": "Primeira linha de defesa. Ganha 2 de escudo empilhável.",
    },
    {
        "id": 26,
        "name": "Arame Farpado",
        "file": "arame_farpado",
        "type": "defense",
        "effect": "shield_team",
        "shield": 1,
        "rarity": "Common",
        "desc": "Teias de aço. Toda a equipe ganha 1 de escudo.",
    },
    {
        "id": 27,
        "name": "Abrigo de Concreto",
        "file": "abrigo_concreto",
        "type": "defense",
        "effect": "shield_self",
        "shield": 4,
        "rarity": "Epic",
        "desc": "Bunker impenetrável. Ganha 4 de escudo.",
    },
    {
        "id": 28,
        "name": "Capacete de Aço",
        "file": "capacete_aco",
        "type": "defense",
        "effect": "shield_self",
        "shield": 1,
        "rarity": "Common",
        "desc": "Simples e eficaz. Ganha 1 de escudo permanente.",
    },
    {
        "id": 29,
        "name": "Casamata",
        "file": "casamata",
        "type": "defense",
        "effect": "shield_self",
        "shield": 3,
        "rarity": "Rare",
        "desc": "Posição defensiva. Ganha 3 de escudo.",
    },
    {
        "id": 30,
        "name": "Escudo Antibomba",
        "file": "escudo_antibomba",
        "type": "defense",
        "effect": "shield_self",
        "shield": 3,
        "rarity": "Rare",
        "desc": "Tecnologia moderna. Absorve o próximo ataque de área (3 de escudo).",
    },
    {
        "id": 31,
        "name": "Linha Defensiva",
        "file": "linha_defensiva",
        "type": "defense",
        "effect": "shield_team",
        "shield": 3,
        "rarity": "Epic",
        "desc": "Doutrina Hindenburg. Toda a equipe ganha 3 de escudo.",
    },

    # =========================================================
    # RECURSOS
    # =========================================================

    {
        "id": 32,
        "name": "Comboio de Suprimentos",
        "file": "comboio_suprimentos",
        "type": "resource",
        "effect": "resource",
        "resource": "food",
        "amount": 3,
        "rarity": "Common",
        "desc": "O sangue da guerra. Sua equipe ganha 3 de comida.",
    },
    {
        "id": 33,
        "name": "Depósito de Munição",
        "file": "deposito_municao",
        "type": "resource",
        "effect": "resource",
        "resource": "ammo",
        "amount": 3,
        "rarity": "Rare",
        "desc": "Arsenal estratégico. Sua equipe ganha 3 de munição.",
    },
    {
        "id": 34,
        "name": "Discurso Motivador",
        "file": "discurso_motivador",
        "type": "resource",
        "effect": "resource",
        "resource": "morale",
        "amount": 3,
        "rarity": "Common",
        "desc": "As palavras certas. Sua equipe ganha 3 de moral.",
    },
    {
        "id": 35,
        "name": "Ajuda Internacional",
        "file": "ajuda_internacional",
        "type": "resource",
        "effect": "resource",
        "resource": "food",
        "amount": 5,
        "rarity": "Rare",
        "desc": "Aliados chegam com ouro. Sua equipe ganha 5 de comida.",
    },
    {
        "id": 36,
        "name": "Produção Industrial",
        "file": "producao_industrial",
        "type": "resource",
        "effect": "resource",
        "resource": "ammo",
        "amount": 4,
        "rarity": "Epic",
        "desc": "Fábricas dia e noite. Sua equipe ganha 4 de munição.",
    },
    {
        "id": 37,
        "name": "Fábrica de Armamentos",
        "file": "fabrica_armamentos",
        "type": "resource",
        "effect": "resource",
        "resource": "ammo",
        "amount": 6,
        "rarity": "Legendary",
        "desc": "Mega-estrutura industrial. Sua equipe ganha 6 de munição.",
    },
    {
        "id": 38,
        "name": "Recrutamento",
        "file": "recrutamento",
        "type": "resource",
        "effect": "resource",
        "resource": "morale",
        "amount": 2,
        "rarity": "Common",
        "desc": "Novos soldados chegam. Sua equipe ganha 2 de moral.",
    },
    {
        "id": 39,
        "name": "Colheita",
        "file": "colheita",
        "type": "resource",
        "effect": "resource",
        "resource": "food",
        "amount": 2,
        "rarity": "Common",
        "desc": "Os campos ainda dão frutos. Sua equipe ganha 2 de comida.",
    },

    # =========================================================
    # ESPIONAGEM
    # =========================================================

    {
        "id": 40,
        "name": "Roubo de Suprimentos",
        "file": "roubo_suprimentos",
        "type": "spy",
        "effect": "steal_resource",
        "resource": "food",
        "amount": 3,
        "rarity": "Rare",
        "desc": "Agentes nas sombras. Rouba 3 de comida do inimigo.",
    },
    {
        "id": 41,
        "name": "Sabotagem",
        "file": "sabotagem",
        "type": "spy",
        "effect": "steal_resource",
        "resource": "ammo",
        "amount": 3,
        "rarity": "Epic",
        "desc": "Uma fábrica explode. Rouba 3 de munição do inimigo.",
    },
    {
        "id": 42,
        "name": "Propaganda",
        "file": "propaganda",
        "type": "spy",
        "effect": "steal_resource",
        "resource": "morale",
        "amount": 3,
        "rarity": "Rare",
        "desc": "Verdade ou mentira. Rouba 3 de moral do inimigo.",
    },
    {
        "id": 43,
        "name": "Código Decifrado",
        "file": "codigo_decifrado",
        "type": "spy",
        "effect": "reveal_intel",
        "rarity": "Legendary",
        "desc": "Quebramos o código. Revela todas as cartas na mão dos inimigos.",
    },
    {
        "id": 44,
        "name": "Agente Infiltrado",
        "file": "agente_infiltrado",
        "type": "spy",
        "effect": "steal_resource",
        "resource": "morale",
        "amount": 2,
        "rarity": "Epic",
        "desc": "Um rosto amigo com intenções mortais. Rouba 2 de moral do inimigo.",
    },
    {
        "id": 45,
        "name": "Interceptação de Rádio",
        "file": "interceptacao_radio",
        "type": "spy",
        "effect": "reveal_intel",
        "rarity": "Rare",
        "desc": "Frequências capturadas. Revela as próximas 3 cartas dos inimigos.",
    },

    # =========================================================
    # HISTÓRICAS
    # =========================================================

    {
        "id": 46,
        "name": "Gás Mostarda",
        "file": "gas_mostarda",
        "type": "historical",
        "effect": "aoe",
        "damage": 3,
        "rarity": "Legendary",
        "desc": "O horror químico. Causa 3 de dano a todos os inimigos vivos.",
    },
    {
        "id": 47,
        "name": "Tanque Mark I",
        "file": "tanque_mark_i",
        "type": "historical",
        "effect": "damage_single",
        "damage": 5,
        "rarity": "Legendary",
        "desc": "1916: o monstro de aço desperta. Causa 5 de dano a um inimigo.",
    },
    {
        "id": 48,
        "name": "Avião de Reconhecimento",
        "file": "aviao_reconhecimento",
        "type": "historical",
        "effect": "reveal_intel",
        "rarity": "Epic",
        "desc": "Olhos nos céus. Revela as cartas na mão de todos os inimigos.",
    },
    {
        "id": 49,
        "name": "Trégua de Natal",
        "file": "tregua_natal",
        "type": "historical",
        "effect": "truce",
        "rounds": 2,
        "rarity": "Legendary",
        "desc": "25/12/1914. Nenhum ataque pode ser realizado pelas próximas 2 rodadas.",
    },
]


# Mapeamento de tipo para cor (usado no front para o badge da carta)
TYPE_COLORS = {
    "attack":    "#8B0000",   # Vermelho escuro
    "heal":      "#2d5a27",   # Verde militar
    "defense":   "#1a3a5c",   # Azul aço
    "resource":  "#8B6914",   # Dourado
    "spy":       "#4a1870",   # Roxo
    "historical": "#6b4c1a",  # Bronze
}

# Mapeamento de raridade para símbolo (exibido no front)
RARITY_SYMBOLS = {
    "Common":    "◆",
    "Rare":      "◆◆",
    "Epic":      "◆◆◆",
    "Legendary": "★",
}


def draw_card():
    """Retorna uma carta aleatória do baralho."""
    return dict(random.choice(CARDS))   # cópia para evitar mutação


def draw_cards(amount: int) -> list:
    """Retorna `amount` cartas aleatórias (com repetição)."""
    return [draw_card() for _ in range(amount)]