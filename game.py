import random
from cards import CARDS

TEAMS = [
    "Aliados",
    "Centrais"
]

CLASSES = [
    "Comandante",
    "Médico",
    "Engenheiro",
    "Espião",
    "Impostor"
]


def assign_teams(players):
    random.shuffle(players)
    half = len(players) // 2
    for i, player in enumerate(players):
        if i < half:
            player.team = "Aliados"
        else:
            player.team = "Centrais"


def assign_classes(players):
    for player in players:
        player.player_class = random.choice(CLASSES)
        if player.player_class == "Comandante":
            player.max_hp = 12
            player.hp = 12
        elif player.player_class == "Espião":
            player.max_hp = 8
            player.hp = 8
        elif player.player_class == "Impostor":
            player.max_hp = 8
            player.hp = 8
            player.shield = 4
        else:
            player.max_hp = 10
            player.hp = 10


# --- Funções de jogo com cartas ---

def play_card(player, card, all_players):
    """Executa o efeito de uma carta jogada com base no parâmetro 'effect'."""
    effect = card['effect']
    
    if effect == 'damage_single':
        # Dano a um inimigo específico
        enemies = [p for p in all_players if p != player and p.alive]
        if enemies:
            target = [p for p in enemies if p.team != player.team and p.alive][0]
            target.hp -= card['damage']
            if target.hp <= 0:
                target.alive = False
            return f"{player.name} causou {card['damage']} de dano a {target.name}"

    elif effect == 'damage':
        # Dano a um inimigo aleatório
        enemies = [p for p in all_players if p != player and p.alive]
        if enemies:
            target = random.choice(enemies)
            target.hp -= card['damage']
            if target.hp <= 0:
                target.alive = False
            return f"{player.name} causou {card['damage']} de dano a {target.name}"

    elif effect == 'aoe':
        # Dano a todos os inimigos
        enemies = [p for p in all_players if p != player and p.alive]
        for target in enemies:
            target.hp -= card['damage']
            if target.hp <= 0:
                target.alive = False
        return f"{player.name} causou {card['damage']} de dano a todos os inimigos"

    elif effect == 'heal_self':
        heal = card.get('heal', 0)
        player.hp = min(player.max_hp, player.hp + heal)
        return f"{player.name} recuperou {heal} de vida"

    elif effect == 'shield_self':
        shield = card.get('shield', 0)
        player.shield += shield
        return f"{player.name} ganhou {shield} de escudo"

    elif effect == 'shield_team':
        shield = card.get('shield', 0)
        for p in all_players:
            if p != player and p.team == player.team and p.alive:
                p.shield += shield
        return f"{player.name} deu {shield} de escudo a equipe"

    elif effect == 'gain_resource':
        resource = card['resource']
        amount = card['amount']
        if not hasattr(player, 'resources'):
            player.resources = {}
        player.resources[resource] = player.resources.get(resource, 0) + amount
        return f"{player.name} ganhou {amount} de {resource}"

    elif effect == 'steal_resource':
        resource = card['resource']
        amount = card['amount']
        enemy_players = [p for p in all_players if p.team != player.team and p.alive]
        if enemy_players:
            target = random.choice(enemy_players)
            if hasattr(target, 'resources') and target.resources.get(resource, 0) > 0:
                steal = min(amount, target.resources.get(resource, 0))
                target.resources[resource] -= steal
                if not hasattr(player, 'resources'):
                    player.resources = {}
                player.resources[resource] = player.resources.get(resource, 0) + steal
                return f"{player.name} roubou {steal} de {resource} de {target.name}"
        return f"{player.name} não conseguiu roubar {resource}"

    elif effect == 'reveal_intel':
        # Revelar cartas dos inimigos
        enemies = [p for p in all_players if p != player and p.team != player.team and p.alive]
        revealed = []
        for enemy in enemies:
            revealed.append(f"{enemy.name}: {len(enemy.hand)} cartas")
        return f"{player.name} revelou: {', '.join(revealed)}"

    elif effect == 'truce':
        # Trégua por um round
        return f"{player.name} ativou trégua por {card.get('rounds', 1)} rodada(s)"

    return f"{player.name} jogou {card['name']}"


def draw_card():
    """Sorteia uma carta do baralho."""
    return random.choice(CARDS)


def draw_cards(amount):
    """Sorteia várias cartas."""
    return [draw_card() for _ in range(amount)]