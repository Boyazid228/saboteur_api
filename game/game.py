import json

from game.dealer import Dealer
from game.board import Board


class Game:
    def __init__(self, lobby):
        self.players = lobby.get_players()
        self.dealer = Dealer()
        self.turn_index = 0
        self.started = False
        self.board = Board()
        self.lobby = lobby

    def start(self):
        self.dealer.start(len(self.players))
        self.started = True
        for player in self.players:
            player_card = self.dealer.player_cards.pop()
            print(player_card)
            game_cards = self.dealer.deal_game_cards()
            player.player_card = player_card
            player.cards = game_cards + [player_card]

    def current_player(self):
        return self.players[self.turn_index]

    def next_turn(self):
        self.turn_index = (self.turn_index + 1) % len(self.players)

    def is_valid_move(self, player_id, move):

        move = json.loads(move)
        card = self.check_card(move["card"], player_id)
        if type(card) is str:
            return False

        self.board.add_item(move["turn"][0], move["turn"][1], card)

        # write crds putting logic
        check = True
        if check:
            self.player_cards_update(self.lobby.get_player(player_id))
        return check

    def check_card(self, id, player_id):
        player = self.lobby.get_player(player_id)
        if player:
            for index, card in enumerate(player.cards):
                if card.id == id:
                    player.cards.pop(index)
                    return card
            return "Card not found in player hand"
        else:
            return "Player not found in Lobby"

    def player_cards_update(self, player):
        card = self.dealer.get_card()
        if card is not None:
            player.cards.append(card)

    def get_allowed_coords(self):
        return [list(coord) for coord in self.board.allowed_coords]


