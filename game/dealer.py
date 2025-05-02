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

    def start(self, player_count):
        self.player_count = player_count
        self.deal_player_cards()
        self.make_path_action_cards()

    def deal_player_cards(self):
        if self.player_count == 3:
            self.player_cards.append(Card(get_random_token(), 'player', json.dumps(
                {"img": "player.jpg", "type": "player",
                 "player": "saboteur",
                 "start": False, "finish": False})))

            for i in range( self.player_count-1):
                self.player_cards.append(Card(get_random_token(), 'player', json.dumps(
                {"img": "player.jpg", "type": "player",
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
            temp.append(self.path_actions_cards.pop())
        return temp

    def show(self):
        print(self.player_cards, self.player_count)
        for i in self.player_cards:
            i.show()

    def get_card(self):
        return self.path_actions_cards.pop() if self.path_actions_cards else None

