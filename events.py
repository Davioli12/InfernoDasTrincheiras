import random

# Eventos aleatórios que podem ocorrer no início de uma nova rodada,
# conforme o manual ("Eventos Aleatórios").

EVENTS = [
    {
        "name": "Chuva Intensa",
        "desc": "A chuva forte reduz o dano de todos os ataques nesta rodada.",
        "effect": "rain"
    },
    {
        "name": "Epidemia",
        "desc": "Uma epidemia se espalha pelas trincheiras. Todos os jogadores vivos perdem 1 de vida.",
        "effect": "epidemic"
    },
    {
        "name": "Reforços",
        "desc": "Reforços chegam à linha de frente. Todas as equipes recebem recursos.",
        "effect": "reinforcements"
    },
    {
        "name": "Bombardeio de Artilharia",
        "desc": "Um bombardeio atinge o campo de batalha. Todos os jogadores vivos sofrem dano.",
        "effect": "artillery"
    }
]

# Chance de um evento ocorrer ao início de uma nova rodada.
EVENT_CHANCE = 0.3


def maybe_trigger_event(room):
    """Decide se um evento ocorre no início de uma nova rodada e já aplica
    seus efeitos imediatos na sala. Retorna o evento escolhido, ou None."""

    room["rain_active"] = False

    if random.random() > EVENT_CHANCE:
        return None

    event = random.choice(EVENTS)
    apply_event(room, event)

    return event


def apply_event(room, event):

    effect = event["effect"]

    if effect == "rain":

        room["rain_active"] = True

    elif effect == "epidemic":

        # Doença ignora a defesa das trincheiras.
        for p in room["players"]:

            if p.alive:

                p.hp = max(0, p.hp - 1)

                if p.hp == 0:
                    p.alive = False

    elif effect == "reinforcements":

        for team_resources in room["resources"].values():

            for key in team_resources:

                team_resources[key] += 2

    elif effect == "artillery":

        # Bombardeio é dano de combate: a defesa das trincheiras ajuda.
        for p in room["players"]:

            if p.alive:
                p.take_damage(2)