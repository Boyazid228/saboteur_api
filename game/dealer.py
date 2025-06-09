import json
import random
import string
from game.cards_data import cards
from game.card import Card


def shuffle_array(arr):
    for i in range(len(arr) - 1, 0, -1):
        j = random.randint(0, i)
        arr[i], arr[j] = arr[j], arr[i]
    return arr


def get_random_token(length=5):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


class Dealer:

    def __init__(self):
        self.players = []
        self.path_actions_cards = []
        self.player_cards = []
        self.player_count = 0
        self.gold_cards = [

            {"img": "gold1.jpg", "type": "gold", "matrix": [], "golds": 1, "action": "", "player": "", "start": False,
             "finish": False},
            {"img": "gold2.jpg", "type": "gold", "matrix": [], "golds": 2, "action": "", "player": "", "start": False,
             "finish": False},
            {"img": "gold3.jpg", "type": "gold", "matrix": [], "golds": 3, "action": "", "player": "", "start": False,
             "finish": False},
        ]
        self.gold_cards_for_players = []

    def start(self, player_count):
        self.player_count = player_count
        self.deal_player_cards()
        self.make_path_action_cards()

    def deal_player_cards(self):
        if self.player_count == 3:
            self.player_cards.append(Card(get_random_token(), 'player', json.dumps(
                {"img": "saboteur.jpg", "type": "player",
                 "player": "saboteur",
                 "start": False, "finish": False})))

            for i in range( self.player_count-1):
                self.player_cards.append(Card(get_random_token(), 'player', json.dumps(
                {"img": "miner.jpg", "type": "player",
                 "player": "player",
                 "start": False, "finish": False})))

        shuffle_array(self.player_cards)

    def make_path_action_cards(self):
        for i in cards:
            if i["type"] in ("path", "action"):
                self.path_actions_cards.append(Card(get_random_token(), i["type"], json.dumps(i)))

        shuffle_array(self.path_actions_cards)

    def deal_game_cards(self):
        temp = []
        for i in range(3):
            if self.path_actions_cards:
                temp.append(self.path_actions_cards.pop())
            else:
                break
        return temp

    def show(self):
        print(self.player_cards, self.player_count)
        for i in self.player_cards:
            i.show()

    def get_card(self):
        return self.path_actions_cards.pop() if self.path_actions_cards else None

    def get_gold_cards(self):
        self.gold_cards_for_players = [random.choices(self.gold_cards, k=1)[0] for _ in range(self.player_count-1)]
        return self.gold_cards_for_players

    def pop_gold(self, gold_count):
        for i, card in enumerate(self.gold_cards_for_players):

            if card['golds'] == int(gold_count):
                return [self.gold_cards_for_players.pop(i)]
        return []

