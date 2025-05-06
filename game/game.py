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
        if self.players[self.turn_index].cards:
            return self.players[self.turn_index]
        else:
            self.next_turn()
            return self.players[self.turn_index]

    def next_turn(self):
        self.turn_index = (self.turn_index + 1) % len(self.players)

    def is_valid_move(self, player_id, move):

        move = json.loads(move)
        card = self.check_card(move["card"], player_id)
        if type(card) is str:
            return False

        check = self.check(move["turn"][0], move["turn"][1], card)
        if check:
            self.player_cards_update(self.lobby.get_player(player_id))
            self.board.add_item(move["turn"][0], move["turn"][1], card)
        return check

    def check(self, x, y, card):

        new_card = json.loads(card.card_data)["matrix"]
        if self.board.has_card_at(x, y):
            return False

        directions = {
            'left': (-1, 0),
            'right': (1, 0),
            'up': (0, 1),
            'down': (0, -1)
        }

        matches = 0

        for dir_name, (dx, dy) in directions.items():
            neighbor = self.board.get_card_at(x + dx, y + dy)
            if neighbor is None:
                continue

            neighbor = json.loads(neighbor.card_data)["matrix"]

            match = True
            if dir_name == 'left':
                for i in range(3):
                    if new_card[i][0] != neighbor[i][2]:
                        match = False
                        break
            elif dir_name == 'right':
                for i in range(3):
                    if new_card[i][2] != neighbor[i][0]:
                        match = False
                        break
            elif dir_name == 'up':
                for i in range(3):
                    if new_card[0][i] != neighbor[2][i]:
                        match = False
                        break
            elif dir_name == 'down':
                for i in range(3):
                    if new_card[2][i] != neighbor[0][i]:
                        match = False
                        break

            if match:
                matches += 1

        return matches > 0

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


