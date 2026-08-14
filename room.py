from player import Player
from cards import CARDS, draw_cards
from game import assign_teams, assign_classes, TEAMS
import os
from dotenv import load_dotenv

load_dotenv()

import random
import string

rooms = {}
code_dev_increase = 0

MIN_PLAYERS_TO_START = 2


def generate_room_code():
    global code_dev_increase

    while True:

        code = ''.join(

            random.choices(

                string.ascii_uppercase +

                string.digits,

                k=6
            )
        )

        if code not in rooms:
        
            code_dev = os.getenv("code")
            
            if code_dev == "build":
                print(f"[SISTEMA]: room code: {code}")
                return code
            else:   
                if code_dev in rooms:
                    code_dev_increase += 1
                    
                    if code_dev[-1].isdigit():
                        code_dev = code_dev[:-1] + str(int(code_dev[-1]) + code_dev_increase)
                    else:
                        code_dev = f"{code_dev}{code_dev_increase}"
                print(f"[SISTEMA]: dev room code: {code_dev}")
                return code_dev


def create_room(room_id, host_sid, max_players=6):

    max_players = max(2, min(8, max_players))

    rooms[room_id] = {

        "host": host_sid,

        "host_id": None,

        "started": False,

        "winner": None,
        "winner_bonus": [],

        "max_players": max_players,

        "players": [],

        "turn_order": [],

        "current_turn": 0,
        
        "truce_rounds": 0,
        
        "deck": [],
        "discard": [],

        "resources": {

            TEAMS[0]: {

                "food": 10,
                "ammo": 10,
                "morale": 10
            },

            TEAMS[1]: {

                "food": 10,
                "ammo": 10,
                "morale": 10
            }
        }
    }


def add_player(

    room_id,

    name,

    sid

):

    room = rooms[room_id]

    if room["started"]:
        return None

    for player in room["players"]:

        if player.name.lower() == name.lower():

            return None

        if player.sid == sid:

            return None

    player = Player(
        name,
        sid
    )
    player.hand = []
    room["players"].append(player)
    return player


def transfer_host(room):
    if not room["players"]:
        room["host"] = None
        room["host_id"] = None
        return None

    new_host = room["players"][-1]
    room["host"] = new_host.sid
    room["host_id"] = new_host.id
    return new_host


def remove_player(sid):

    for room_id, room in list(rooms.items()):

        for player in room["players"][:]:

            if player.sid == sid:

                room["players"].remove(player)

                if player.id in room["turn_order"]:
                    room["turn_order"].remove(player.id)

                if room["host"] == sid:
                    transfer_host(room)

                if room["started"]:
                    winner = check_winner(room)
                    if winner:
                        room["winner"] = winner["team"]
                        room["winner_bonus"] = winner.get("bonus_winners", [])
                        room["started"] = False

                if not room["players"]:
                    try:
                        del rooms[room_id]
                    except KeyError:
                        pass

                return room_id

    return None


def get_player_by_sid(room, sid):

    for player in room["players"]:

        if player.sid == sid:
            return player

    return None


def get_player_by_id(room, player_id):

    for player in room["players"]:

        if player.id == player_id:
            return player

    return None


def start_game(room):

    players = room["players"]

    if room["started"]:
        return False, "O jogo já foi iniciado."

    if len(players) < MIN_PLAYERS_TO_START:
        return False, "São necessários pelo menos 2 jogadores."

    assign_teams(players)
    assign_classes(players)

    room["turn_order"] = [p.id for p in players]
    random.shuffle(room["turn_order"])

    room["current_turn"] = 0
    room["started"] = True
    room["winner"] = None
    room["winner_bonus"] = []
    room["round_count"] = 0
    room["deck"] = CARDS.copy()

    random.shuffle(
        room["deck"]
    )

    room["discard"] = []

    for player in players:
        player.hand = [
            draw_from_deck(room)
            for _ in range(3)
        ]

    return True, None

def draw_from_deck(room):

    if not room["deck"]:

        room["deck"] = room["discard"]

        room["discard"] = []

        random.shuffle(
            room["deck"]
        )

    if not room["deck"]:
        return None

    return room["deck"].pop()

def current_player(room):

    if not room["turn_order"]:
        return None

    turn_index = room["current_turn"] % len(room["turn_order"])
    player_id = room["turn_order"][turn_index]

    return get_player_by_id(room, player_id)


def advance_turn(room):

    if not room["turn_order"]:
        return

    for _ in range(len(room["turn_order"])):

        room["current_turn"] = (room["current_turn"] + 1) % len(room["turn_order"])

        nxt = current_player(room)

        if nxt and nxt.alive:
            return


def resolve_winner(room):

    for team, res in room["resources"].items():

        if (

            res["food"] <= 0

            or

            res["ammo"] <= 0

            or

            res["morale"] <= 0

        ):

            enemy = [

                t

                for t in room["resources"]

                if t != team

            ]

            return enemy[0]

    teams_alive = set(

        p.team

        for p in room["players"]

        if p.alive and p.team

    )

    if len(teams_alive) == 1:

        return teams_alive.pop()

    return None


def check_winner(room, finisher=None):
    base_winner = resolve_winner(room)

    if not base_winner:
        return None

    if (
        finisher
        and getattr(finisher, "player_class", None) == "Impostor"
        and getattr(finisher, "alive", True)
    ):
        finisher_team = getattr(finisher, "team", None)
        if finisher_team:
            enemy_team = next(
                (team for team in room["resources"] if team != finisher_team),
                None
            )
            if enemy_team:
                return {
                    "team": enemy_team,
                    "bonus_winners": [getattr(finisher, "name", "Impostor")]
                }

    return {
        "team": base_winner,
        "bonus_winners": []
    }

def room_to_dict(room, viewer_sid=None):

    return {

        "host": room["host"],

        "host_id": room.get("host_id"),

        "started": room["started"],

        "winner": room.get("winner"),
        "winner_bonus": room.get("winner_bonus", []),

        "players": [

            p.to_dict(reveal_hand=(p.sid == viewer_sid))

            for p in room["players"]
        ],

        "resources": room["resources"],

        "turn_order": room["turn_order"],

        "current_player_id": (

            current_player(room).id

            if room["started"] and current_player(room)

            else None
        ),

        "phase": (
            "Jogando"
            if room["started"]
            else "Lobby"
        )
    }