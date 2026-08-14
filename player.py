import uuid

class Player:

    def __init__(self, name, sid):

        self.id = str(uuid.uuid4())

        self.sid = sid

        self.name = name

        self.team = None

        self.player_class = None

        self.hp = 10
        self.max_hp = 10

        self.hand = []

        self.alive = True
        
        self.shield = 0

    def to_dict(self, reveal_hand=False):

        return {

            "id": self.id,

            "name": self.name,

            "team": self.team,

            "class": self.player_class,

            "hp": self.hp,

            "max_hp": self.max_hp,


            "alive": self.alive, "shield": self.shield,

            "hand": self.hand if reveal_hand else [],

            "hand_count": len(self.hand)
        }