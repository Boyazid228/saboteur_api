import json

import game.board
from game.dealer import Dealer
from game.board import Board
import heapq


class Game:
    def __init__(self, lobby):
        self.players = lobby.get_players()
        self.dealer = Dealer()
        self.turn_index = 0
        self.started = False
        self.board = Board()
        self.lobby = lobby
        self.DIRECTIONS = {
            "up": (0, 1),
            "down": (0, -1),
            "left": (-1, 0),
            "right": (1, 0),
        }
        self.allowed_coords = {(0, 1), (1, 0), (-1, 0), (0, -1)}
        self.need_check_finish = []
        self.need_check_finish_card = []
        self.START_CARD = (0, 0)
        self.FINISH_CARDS = [(4, 2), (4, 0), (4, -2)]
        self.finish = False
        self.winner = None
        self.last_action_player = None

    def start(self):
        self.dealer.start(len(self.players))
        self.started = True
        for player in self.players:
            player_card = self.dealer.player_cards.pop()
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
        player = self.lobby.get_player(player_id)
        if type(card) is str:
            return False
        if not player:
            return False

        if 'type' in move and move['type'] == 'trash':
            self.remove_card(player, card)
            return True

        if card.type == "path":
            if player.status != "Normal":
                return False

            check = self.check(move["turn"][0], move["turn"][1], card)
            if check:
                player.remove_card(card)

                self.player_cards_update(self.lobby.get_player(player_id))
                self.add_item(move["turn"][0], move["turn"][1], card)

                path = self.find_path_a_star()
            return check
        elif card.type == "action":

            if card.get_data()["action"] == "see_map":
                if player.status != "Normal":
                    return False
                see_card = self.board.BOARD[(move["turn"][0], move["turn"][1])]
                player.see_card = see_card
            elif card.get_data()["action"] == "rockfall":
                if player.status != "Normal":
                    return False
                if not self.board.remove_element(move["turn"][0], move["turn"][1]):
                    return False
                else:
                    self.update_allowed_coords_after_action_card()
            else:
                if card.get_data()["action"] == "break_cart":
                    player_to = self.lobby.get_player(move["turn"][0])
                    player_to.cart = False
                    player_to.status = "Blocked"
                    self.last_action_player = player_to
                elif card.get_data()["action"] == "break_lantern":
                    player_to = self.lobby.get_player(move["turn"][0])
                    player_to.lantern = False
                    player_to.status = "Blocked"
                    self.last_action_player = player_to
                elif card.get_data()["action"] == "break_pickaxe":
                    player_to = self.lobby.get_player(move["turn"][0])
                    player_to.pickaxe = False
                    player_to.status = "Blocked"
                    self.last_action_player = player_to
                elif card.get_data()["action"] == "fix_lantern" or move["turn"][1] == "lantern":
                    player_to = self.lobby.get_player(move["turn"][0])
                    player_to.lantern = True
                    player_to.check_status()
                    self.last_action_player = player_to
                elif card.get_data()["action"] == "fix_pickaxe" or move["turn"][1] == "pickaxe":
                    player_to = self.lobby.get_player(move["turn"][0])
                    player_to.pickaxe = True
                    player_to.check_status()
                    self.last_action_player = player_to
                elif card.get_data()["action"] == "fix_cart" or move["turn"][1] == "cart":
                    player_to = self.lobby.get_player(move["turn"][0])
                    player_to.cart = True
                    player_to.check_status()
                    self.last_action_player = player_to

            player.remove_card(card)
            self.player_cards_update(self.lobby.get_player(player_id))
            return True
        else:
            return False

    def remove_card(self, player, card):
        player.remove_card(card)
        self.player_cards_update(self.lobby.get_player(player.id))

    def update_allowed_coords_after_action_card(self):
        self.allowed_coords.clear()
        check_coords = set()
        for (dx, dy), card in self.board.BOARD.items():
            path = self.find_path_a_star([(dx, dy)])
            if path is not None:
                for coord in path:
                    check_coords.add(coord)

        for (z, w) in check_coords:
            self.update_allowed_coords(z, w, self.board.BOARD[(z, w)])

    def check(self, x, y, card):

        new_card = json.loads(card.card_data)["matrix"]
        if self.board.has_card_at(x, y):
            return False

        directions = {
            'left': (-1, 0),
            'right': (1, 0),
            'down': (0, -1),
            'up': (0, 1)

        }

        matches = 0
        neighbor_count = 0
        neighbor_ = None

        for dir_name, (dx, dy) in directions.items():
            neighbor = self.board.get_card_at(x + dx, y + dy)
            if neighbor is None:
                continue

            is_finish = json.loads(neighbor.card_data)['finish']
            if is_finish and not (x + dx, y + dy) in self.board.show_finish:
                self.need_check_finish.append((x + dx, y + dy))
                self.need_check_finish_card.append([x + dx, y + dy, neighbor])
                continue

            neighbor = self.get_oriented_matrix(neighbor)

            match = True
            if dir_name == 'left':

                if (new_card[1][2] if card.is_rotated else new_card[1][0]) != neighbor[1][2]:
                    match = False

            elif dir_name == 'right':

                if (new_card[1][0] if card.is_rotated else new_card[1][2]) != neighbor[1][0]:
                    match = False

            elif dir_name == 'up':

                if (new_card[2][1] if card.is_rotated else new_card[0][1]) != neighbor[2][1]:
                    match = False

            elif dir_name == 'down':
                if (new_card[0][1] if card.is_rotated else new_card[2][1]) != neighbor[0][1]:
                    match = False

            if match:
                matches += 1
            neighbor_count += 1
            neighbor_ = neighbor

        if neighbor_count == 1 and neighbor_[1][1] == 0:
            return False
        if neighbor_count != matches:
            return False
        return matches > 0

    def check_card(self, id, player_id):
        player = self.lobby.get_player(player_id)
        if player:
            for index, card in enumerate(player.cards):
                if card.id == id:
                    return card
            return "Card not found in player hand"
        else:
            return "Player not found in Lobby"

    def player_cards_update(self, player):
        card = self.dealer.get_card()
        if card is not None:
            player.cards.append(card)

    def get_allowed_coords(self):
        return [list(coord) for coord in self.allowed_coords]

    def is_connected(self, from_matrix, to_matrix, direction):
        try:
            if from_matrix[1][1] != 1 or to_matrix[1][1] != 1:
                return False

            if direction == 'down':
                return from_matrix[2][1] == 1 and to_matrix[0][1] == 1
            elif direction == 'up':
                return from_matrix[0][1] == 1 and to_matrix[2][1] == 1
            elif direction == 'left':
                return from_matrix[1][0] == 1 and to_matrix[1][2] == 1
            elif direction == 'right':
                return from_matrix[1][2] == 1 and to_matrix[1][0] == 1

            return False
        except (IndexError, TypeError) as e:
            return False

    def get_oriented_matrix(self, card):
        matrix = card.get_data().get("matrix")
        if not matrix:
            return None
        if getattr(card, "is_rotated", False):
            return [row[::-1] for row in matrix[::-1]]
        return matrix

    def find_path_a_star(self, finishes=None):
        board = self.board.get_board_copy()
        if finishes is None:
            finishes = self.FINISH_CARDS

        start = self.START_CARD

        if start is None or not finishes:
            return None

        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        open_set = []
        heapq.heappush(open_set, (0, start, [start]))
        g_score = {start: 0}
        visited = set()
        while open_set:
            _, current, path = heapq.heappop(open_set)

            if current in visited:
                continue
            visited.add(current)

            if current in finishes:
                return path
            current_card = board.get(current)
            from_matrix = self.get_oriented_matrix(current_card)
            if not from_matrix:
                continue
            for direction, (dx, dy) in self.DIRECTIONS.items():
                neighbor = (current[0] + dx, current[1] + dy)
                neighbor_card = board.get(neighbor)
                if not neighbor_card:
                    continue

                to_matrix = self.get_oriented_matrix(neighbor_card)
                if not to_matrix:
                    continue
                if self.is_connected(from_matrix, to_matrix, direction):
                    tentative_g_score = g_score[current] + 1
                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        g_score[neighbor] = tentative_g_score
                        f_score = tentative_g_score + min(heuristic(neighbor, f) for f in finishes)
                        heapq.heappush(open_set, (f_score, neighbor, path + [neighbor]))

        return None

    def add_item(self, x, y, card):
        if (x, y) not in self.board.BOARD:
            self.board.BOARD[(x, y)] = card
            #self.update_allowed_coords(x, y, card)
            for i in range(len(self.need_check_finish)):
                x = self.need_check_finish_card[i][0]
                y = self.need_check_finish_card[i][1]
                finish_card = self.need_check_finish_card[i][2]
                path = self.find_path_a_star()
                if path is not None and not (x, y) in self.board.show_finish and path[-1] == (x, y):
                    self.FINISH_CARDS.remove((x, y))
                    self.board.show_finish.append((x, y))
                    self.finish = self.check_finish_card(x, y, finish_card)
                    if not self.finish:
                        direct = (path[-2][0] - path[-1][0], path[-2][1] - path[-1][1])
                        board_card = self.board.BOARD[path[-1]]
                        if finish_card.id == "finish1":
                            board_card.set_matrix([[0, 1, 0], [0, 1, 1], [0, 0, 0]])
                            if direct != (0, 1) and direct != (1, 0):
                                board_card.is_rotated = True

                        else:
                            print(direct)
                            board_card.set_matrix([[0, 1, 0], [1, 1, 0], [0, 0, 0]])
                            if direct != (-1, 0) and direct != (0, 1):
                                board_card.is_rotated = True

                    #self.update_allowed_coords(x, y, finish_card)

            self.need_check_finish_card = []
            self.need_check_finish = []
            self.update_allowed_coords_after_action_card()
        return self.board.BOARD

    def update_allowed_coords(self, x, y, card):
        coord = (x, y)
        self.allowed_coords.discard(coord)
        direction = [[-1, 0], [1, 0], [0, 1], [0, -1]]
        possible_path = [[1, 0], [1, 2], [0, 1], [2, 1]]
        matrix = card.get_data()["matrix"]
        if matrix[1][1] != 0:
            for index, i in enumerate(direction):
                if (x + i[0], y + i[1]) in self.board.BOARD:
                    continue

                px, py = possible_path[index]
                value = matrix[2 - px][2 - py] if card.is_rotated else matrix[px][py] #
                if value:
                    self.allowed_coords.add((x + i[0], y + i[1]))

    def check_finish_card(self, x, y, card):
        card_data = card.get_data()
        return (
                (x, y) in self.board.BOARD and
                self.board.BOARD[(x, y)] == card and
                card_data["finish"] and
                card_data["gold"]
        )

    def get_opponents(self, player):
        player = self.lobby.get_player(player)
        return [x for x in self.players if x != player]

    def set_gold_card(self, gold_count, player_id):
        p = self.lobby.get_player(player_id)
        p.gold_cars = self.dealer.pop_gold(gold_count)

    def winner_gold(self):
        max_g = 0
        winners = []
        print(self.players)
        for player in self.players:
            local_max = 0
            print(player.get_player_json())
            for card in player.gold_cars:
                local_max += card.get('golds', 0)
                print(local_max)
            print(local_max, max_g)
            print(winners)
            if local_max > max_g:
                max_g = local_max
                winners = [player.get_player_json()]
            elif local_max == max_g and local_max > 0:
                winners.append(player.get_player_json())

            print(local_max, max_g)
            print(winners)

        return winners if winners else None

