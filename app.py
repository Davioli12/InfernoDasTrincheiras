from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from cards import draw_cards
import threading
import sys
import time
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(
    filename="InfernoDasTrincheiras.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

from room import (
    rooms,
    create_room,
    generate_room_code,
    add_player,
    remove_player,
    room_to_dict,
    get_player_by_sid,
    start_game,
    current_player,
    advance_turn,
    check_winner
)

logging.info("Imports com sucesso")

app = Flask(__name__)
app.config["SECRET_KEY"] = "trincheiras"

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading"
)

logging.info("Configurações aplicadas")

def is_dev_name(name):
    configured_name = (os.getenv("dev_name") or "").strip()
    return bool(configured_name) and str(name or "").strip().lower() == configured_name.lower()


def is_dev_player(player):
    return bool(getattr(player, "is_dev", False)) or is_dev_name(getattr(player, "name", ""))


def emit_dev_access(player):
    if not player or not is_dev_player(player):
        return

    socketio.emit(
        "dev_access",
        {
            "enabled": True,
            "commands": ["set_resource", "set_hp", "finish_game"]
        },
        room=player.sid
    )


# ==========================
# HELPER: BROADCAST
# ==========================

def broadcast_room_state(room_id):
    """Envia o estado da sala para cada jogador individualmente,
    revelando a mão apenas para o próprio dono dela."""

    if room_id not in rooms:
        return

    room = rooms[room_id]

    for player in room["players"]:

        socketio.emit(
            "room_update",
            room_to_dict(room, viewer_sid=player.sid),
            room=player.sid
        )


# ==========================
# HELPER: LOG DE EVENTO
# ==========================

def log_event(room_id, message):
    """Envia uma mensagem de log para todos na sala."""
    socketio.emit(
        "game_log",
        {"message": message},
        room=room_id
    )


# ==========================
# ROTAS
# ==========================

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/restart")

def _restart():
    # Aguarda pequeno atraso para permitir que a resposta HTTP seja enviada
    time.sleep(0.5)

    logging.warning("RESTART DO SERVIDOR CHAMADO...")

    # Re-executa o processo Python atual com os mesmos argumentos
    try:
        logging.warning("Executando Novamente...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        logging.error(f"Erro ao executar: {e}")
        # Se execv falhar, força encerramento (o processo externo pode reiniciar)
        os._exit(1)

    threading.Thread(target=_restart, daemon=True).start()

    return "Reiniciando servidor...", 200
    


# ==========================
# CRIAR SALA
# ==========================

@socketio.on("create_room")
def create_room_event(data):

    name = (data.get("name") or "").strip()

    if not name:
        emit("error_message", {"message": "Nome inválido."})
        return

    max_players = data.get("max_players", 6)

    try:
        max_players = int(max_players)
    except (TypeError, ValueError):
        max_players = 6

    room_id = generate_room_code()

    create_room(room_id, request.sid, max_players)

    player = add_player(room_id, name, request.sid)

    if player is None:
        emit("error_message", {"message": "Não foi possível criar a sala."})
        return

    rooms[room_id]["host_id"] = player.id
    player.is_dev = is_dev_name(name)

    join_room(room_id)
    emit_dev_access(player)

    emit(
        "room_created",
        {
            "room": room_id,
            "player_id": player.id,
            "game": room_to_dict(rooms[room_id], viewer_sid=request.sid)
        }
    )

    broadcast_room_state(room_id)


# ==========================
# ENTRAR EM SALA
# ==========================

@socketio.on("join_room_game")
def join_room_game(data):

    room_id = (data.get("room") or "").upper()
    name    = (data.get("name") or "").strip()

    if not name:
        emit("error_message", {"message": "Nome inválido."})
        return

    if room_id not in rooms:
        emit("error_message", {"message": "Sala não encontrada."})
        return

    room = rooms[room_id]

    if room["started"]:
        emit("error_message", {"message": "O jogo já começou."})
        return

    if len(room["players"]) >= room["max_players"]:
        emit("error_message", {"message": "Sala cheia."})
        return

    player = add_player(room_id, name, request.sid)

    if player is None:
        emit("error_message", {"message": "Nome já utilizado ou jogador já conectado."})
        return

    player.is_dev = is_dev_name(name)

    join_room(room_id)
    emit_dev_access(player)

    emit("room_joined", {"room": room_id, "player_id": player.id})

    broadcast_room_state(room_id)


@socketio.on("list_lobby_rooms")
def list_lobby_rooms():
    available_rooms = []

    for room_id, room in rooms.items():
        if not room["started"] and len(room["players"]) < room["max_players"]:
            available_rooms.append({
                "room": room_id,
                "players": len(room["players"]),
                "max_players": room["max_players"]
            })

    emit("lobby_rooms", {"rooms": available_rooms})


@socketio.on("leave_room")
def leave_room_event(data):
    room_id = (data.get("room") or "").upper()

    if room_id not in rooms:
        emit("error_message", {"message": "Sala não encontrada."})
        return

    leave_room(room_id)
    remove_player(request.sid)
    emit("left_room", {"room": room_id})

    if room_id in rooms:
        broadcast_room_state(room_id)
        # remove finished room if there is a winner
        if rooms[room_id].get("winner"):
            try:
                del rooms[room_id]
            except Exception:
                pass


# ==========================
# INICIAR JOGO
# ==========================

@socketio.on("start_game")
def start_game_event(data):

    room_id = data.get("room")

    if room_id not in rooms:
        return

    room = rooms[room_id]

    if request.sid != room["host"]:
        emit("error_message", {"message": "Apenas o anfitrião pode iniciar o jogo."})
        return

    ok, error = start_game(room)

    if not ok:
        emit("error_message", {"message": error})
        return

    log_event(room_id, "⚔️ A partida começou!")
    broadcast_room_state(room_id)


# ==========================
# JOGAR CARTA
# ==========================
@socketio.on("game_info")
def send_game_info():
    
    """Envia informações do jogo para todos os jogadores (para debug)."""
    for room_id, room in rooms.items():
        socketio.emit(
            "game_info",
            {
                "room": room_id,
                "players": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "team": p.team,
                        "hp": p.hp,
                        "max_hp": p.max_hp,
                        "alive": p.alive,
                        "hand_size": len(p.hand),
                        "shield": getattr(p, "shield", 0)
                    }
                    for p in room["players"]
                ],
                "resources": room["resources"],
                "truce_rounds": room.get("truce_rounds", 0),
                "current_turn_player_id": current_player(room).id if current_player(room) else None,
                "winner": room.get("winner")
            },
            room=room_id
        )

@socketio.on("dev_command")
def dev_command(data):
    room_id = (data.get("room") or "").strip()

    if room_id not in rooms:
        emit("error_message", {"message": "Sala não encontrada."})
        return

    room = rooms[room_id]
    player = get_player_by_sid(room, request.sid)

    if not player or not is_dev_player(player):
        emit("error_message", {"message": "Acesso de console negado."})
        return

    command = (data.get("command") or "").strip()

    if command == "set_resource":
        team = data.get("team")
        resource = data.get("resource")
        amount = int(data.get("amount", 0))

        if team in room["resources"] and resource in room["resources"][team]:
            room["resources"][team][resource] = amount
            log_event(room_id, f"🛠️ {player.name} alterou {resource} de {team} para {amount}.")
            broadcast_room_state(room_id)
            send_game_info()
        else:
            emit("error_message", {"message": "Equipe ou recurso inválido."})

    elif command == "set_hp":
        target_player = next((p for p in room["players"] if p.id == data.get("player_id")), None)
        if not target_player:
            emit("error_message", {"message": "Jogador não encontrado."})
            return

        hp = max(0, int(data.get("hp", 0)))
        target_player.hp = hp
        target_player.alive = hp > 0
        log_event(room_id, f"🛠️ {player.name} definiu a vida de {target_player.name} para {hp}.")
        broadcast_room_state(room_id)
        send_game_info()

    elif command == "finish_game":
        team = data.get("team")
        if team in room["resources"]:
            room["winner"] = team
            room["winner_bonus"] = []
            room["started"] = False
            log_event(room_id, f"🛠️ {player.name} encerrou a partida com vitória de {team}.")
            broadcast_room_state(room_id)
            send_game_info()
            # Remove room after notifying players so code can be reused
            if room_id in rooms:
                try:
                    del rooms[room_id]
                except Exception:
                    pass
        else:
            emit("error_message", {"message": "Equipe inválida."})

    else:
        emit("error_message", {"message": "Comando inválido."})


@socketio.on("play_card")
def play_card(data):

    room_id = data.get("room")
    card_id = data.get("card_id")

    if room_id not in rooms:
        return

    room = rooms[room_id]

    if not room["started"]:
        emit("error_message", {"message": "O jogo ainda não começou."})
        return

    player = get_player_by_sid(room, request.sid)

    if not player or not player.alive:
        return

    turn_player = current_player(room)

    if not turn_player or turn_player.sid != request.sid:
        emit("error_message", {"message": "Não é a sua vez."})
        return

    # Localiza a carta na mão do jogador
    selected_card = next(
        (c for c in player.hand if c["id"] == card_id),
        None
    )

    if not selected_card:
        return

    effect    = selected_card.get("effect")
    own_team  = player.team
    team_names = list(room["resources"].keys())
    enemy_team = next((t for t in team_names if t != own_team), None)

    # ----------------------------------------------------------
    # TRÉGUA: bloqueia ataques enquanto ativa
    # ----------------------------------------------------------

    if effect in ("attack", "aoe", "damage_single") and room.get("truce_rounds", 0) > 0:
        emit("error_message", {"message": "⚠️ Uma trégua está ativa. Ataques bloqueados."})
        return

    # ----------------------------------------------------------
    # PROCESSAR EFEITO
    # ----------------------------------------------------------

    if effect == "heal_self" or effect == "heal":
        # Verifica custo (ex: Hospital Militar custa food)
        cost = selected_card.get("cost", {})

        for resource, amount in cost.items():
            if room["resources"][own_team].get(resource, 0) < amount:
                emit("error_message", {"message": f"Recursos insuficientes ({resource})."})
                return

        for resource, amount in cost.items():
            room["resources"][own_team][resource] -= amount

        heal = selected_card.get("heal", 2)
        player.hp = min(player.max_hp, player.hp + heal)

        log_event(room_id, f"💊 {player.name} usou {selected_card['name']} e recuperou {heal} de vida.")

    # ----------------------------------------------------------

    elif effect == "shield_self":
        # Escudo apenas para o jogador atual
        shield = selected_card.get("shield", 1)
        player.shield = getattr(player, "shield", 0) + shield

        log_event(room_id, f"🛡️ {player.name} usou {selected_card['name']} e ganhou {shield} de escudo.")

    # ----------------------------------------------------------

    elif effect == "shield_team":
        # Escudo para todos os aliados vivos
        shield = selected_card.get("shield", 1)

        for p in room["players"]:
            if p.team == own_team and p.alive:
                p.shield = getattr(p, "shield", 0) + shield

        log_event(room_id, f"🛡️ {player.name} usou {selected_card['name']} — equipe {own_team} ganhou {shield} de escudo.")

    # ----------------------------------------------------------

    elif effect == "resource":
        # Ganho de recurso para a equipe (efeito correto para cartas de recurso)
        resource = selected_card.get("resource", "food")
        amount   = selected_card.get("amount", 1)

        room["resources"][own_team][resource] = \
            room["resources"][own_team].get(resource, 0) + amount

        log_event(room_id, f"📦 {player.name} usou {selected_card['name']} — equipe {own_team} ganhou {amount} de {resource}.")

    # ----------------------------------------------------------

    elif effect in ("steal_resource", "steal"):
        resource = selected_card.get("resource", "food")
        amount   = selected_card.get("amount", 1)

        available = room["resources"].get(enemy_team, {}).get(resource, 0)
        stolen    = min(amount, available)

        room["resources"][enemy_team][resource]  = available - stolen
        room["resources"][own_team][resource]    = \
            room["resources"][own_team].get(resource, 0) + stolen

        log_event(room_id, f"🕵️ {player.name} usou {selected_card['name']} — roubou {stolen} de {resource} dos {enemy_team}.")

    # ----------------------------------------------------------

    elif effect in ("attack", "damage_single"):
        target = next(
            (p for p in room["players"] if p.team == enemy_team and p.alive),
            None
        )

        if not target:
            emit("error_message", {"message": "Nenhum inimigo disponível."})
            return

        damage = selected_card.get("damage", 1)

        # Absorve com escudo primeiro
        shield_absorbed = 0
        if getattr(target, "shield", 0) > 0:
            shield_absorbed = min(target.shield, damage)
            target.shield  -= shield_absorbed
            damage         -= shield_absorbed

        target.hp = max(0, target.hp - damage)

        log_msg = f"⚔️ {player.name} atacou {target.name} com {selected_card['name']} — {damage} de dano"
        if shield_absorbed:
            log_msg += f" ({shield_absorbed} absorvido pelo escudo)"
        log_event(room_id, log_msg + ".")

        if target.hp <= 0:
            target.alive = False
            socketio.emit(
                "player_eliminated",
                {"player_id": target.id, "name": target.name},
                room=room_id
            )
            log_event(room_id, f"💀 {target.name} foi eliminado!")

    # ----------------------------------------------------------

    elif effect == "aoe":
        damage  = selected_card.get("damage", 1)
        targets = [p for p in room["players"] if p.team == enemy_team and p.alive]

        if not targets:
            emit("error_message", {"message": "Nenhum inimigo disponível."})
            return

        eliminated = []

        for t in targets:
            dmg = damage
            if getattr(t, "shield", 0) > 0:
                absorbed   = min(t.shield, dmg)
                t.shield  -= absorbed
                dmg        -= absorbed

            t.hp = max(0, t.hp - dmg)

            if t.hp <= 0:
                t.alive = False
                eliminated.append(t)

        log_event(room_id,
            f"💥 {player.name} usou {selected_card['name']} — {damage} de dano em área nos {enemy_team}."
        )

        for t in eliminated:
            socketio.emit(
                "player_eliminated",
                {"player_id": t.id, "name": t.name},
                room=room_id
            )
            log_event(room_id, f"💀 {t.name} foi eliminado!")

    # ----------------------------------------------------------

    elif effect == "reveal_intel":
        enemy_hands = [
            {"player": p.name, "cards": p.hand}
            for p in room["players"]
            if p.team == enemy_team and p.alive
        ]

        emit("intel_revealed", {"players": enemy_hands}, room=player.sid)
        log_event(room_id, f"🔍 {player.name} usou {selected_card['name']} — informações inimigas reveladas.")

    # ----------------------------------------------------------

    elif effect == "reveal":
        for p in room["players"]:
            if p.team == enemy_team and p.alive:
                emit(
                    "reveal_player",
                    {
                        "player_id": p.id,
                        "class": getattr(p, "player_class", None),
                        "hp": p.hp,
                        "max_hp": p.max_hp,
                        "shield": getattr(p, "shield", 0)
                    },
                    room=player.sid
                )

        log_event(room_id, f"🔍 {player.name} revelou os inimigos.")

    # ----------------------------------------------------------

    elif effect == "truce":
        rounds = selected_card.get("rounds", 1)
        room["truce_rounds"] = rounds

        log_event(room_id, f"☮️ {player.name} jogou {selected_card['name']} — trégua por {rounds} rodada(s)!")

    # ----------------------------------------------------------
    # Remove a carta usada e compra uma nova
    # ----------------------------------------------------------

    player.hand.remove(selected_card)
    player.hand.append(draw_cards(1)[0])

    # Verifica vencedor
    winner = check_winner(room, finisher=player)

    if winner:
        room["winner"] = winner["team"]
        room["winner_bonus"] = winner.get("bonus_winners", [])
        room["started"] = False
        if winner.get("bonus_winners"):
            log_event(room_id, f"🏆 Fim de jogo! Vencedor: {winner['team']} (com {', '.join(winner['bonus_winners'])})")
        else:
            log_event(room_id, f"🏆 Fim de jogo! Vencedor: {winner['team']}!")

    else:
        advance_turn(room)

        # Decrementa trégua ao final do turno
        if room.get("truce_rounds", 0) > 0:
            room["truce_rounds"] -= 1

    broadcast_room_state(room_id)
    
    send_game_info()
    # Se houve vencedor, removemos a sala para liberar o código e não mostrar em lista
    if winner and room_id in rooms:
        try:
            del rooms[room_id]
        except Exception:
            pass


# ==========================
# DESCONECTAR
# ==========================

@socketio.on("disconnect")
def disconnect_player():

    room_id = remove_player(request.sid)

    if not room_id:
        return

    if room_id not in rooms:
        return

    broadcast_room_state(room_id)
    # remove finished room if there is a winner
    if room_id in rooms and rooms[room_id].get("winner"):
        try:
            del rooms[room_id]
        except Exception:
            pass


# ==========================
# INICIAR SERVIDOR
# ==========================
if __name__ == "__main__":
    
    logging.info("Iniciando Servidor")

    HOST = str(os.getenv("host", "127.0.0.1"))
    PORT = int(os.getenv("port", 5000))
    DEBUG = bool(os.getenv("debug", "False").lower() in ("true", "1", "t"))

    logging.info(f"Rodando em: {HOST}:{PORT}")
    logging.info(f"DebugMode: {DEBUG}")

    socketio.run(
        app,
        host=HOST,
        port=PORT,
        debug=DEBUG
    )