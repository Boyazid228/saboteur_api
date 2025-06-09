from game.card import Card
import json
from collections import deque
import heapq
import copy


class Board:
    def __init__(self):
        self.BOARD = {
            (0, 0): Card("start", 'path',
                         json.dumps({"img": "start.jpg", "type": "path", "matrix": [[0, 1, 0], [1, 1, 1], [0, 1, 0]],
                                     "gols": 0,
                                     "action": "",
                                     "player": "", "start": True, "finish": False})),
            (8, 2): Card("finish1", 'path',
                         json.dumps({"img": "stone.jpg", "type": "path", "matrix": [[0, 1, 0], [1, 1, 1], [0, 1, 0]],
                                     "gold": 0,
                                     "action": "",
                                     "player": "", "start": False, "finish": True})),
            (8, 0): Card("finish2", 'path',
                         json.dumps(
                             {"img": "gold.jpg", "type": "path", "matrix": [[0, 1, 0], [1, 1, 1], [0, 1, 0]], "gold": 1,
                              "action": "",
                              "player": "", "start": False, "finish": True})),
            (8, -2): Card("finish3", 'path',
                          json.dumps({"img": "stone2.jpg", "type": "path", "matrix": [[0, 1, 0], [1, 1, 1], [0, 1, 0]],
                                      "gold": 0,
                                      "action": "",
                                      "player": "", "start": False, "finish": True})),

        }

        self.show_finish = []
        self.HIDDEN_CARDS = [(8, 2), (8, 0), (8, -2)]

    def to_json(self, board):
        return {
            f"{x},{y}": value.get_json()
            for (x, y), value in board.items()
        }

    def to_list(self):
        return [
            {"x": x, "y": y, "value": value.get_json()}
            for (x, y), value in self.BOARD.items()
        ]

    def get_hidden_card(self):
        return Card("hidden", 'path', json.dumps({
            "img": "hidden.jpg", "type": "path", "matrix": [],
            "gols": 0, "action": "", "player": "", "start": False, "finish": False
        }))

    def get_board(self):
        temp = copy.deepcopy(self.BOARD)

        for pos in self.HIDDEN_CARDS:
            if pos not in self.show_finish:
                temp[pos] = self.get_hidden_card()

        return self.to_json(temp)

    def has_card_at(self, x, y):
        return (x, y) in self.BOARD

    def get_card_at(self, x, y):
        return self.BOARD.get((x, y))

    def get_board_copy(self):
        return copy.deepcopy(self.BOARD)

    def remove_element(self, x, y):
        if self.BOARD.get((x, y)):
            del self.BOARD[(x, y)]
            return True
        else:
            return False

    def show(self, size=9):
        # size — радиус сетки: от -size до +size
        for y in range(size, -1 - size, -1):  # от +size до -size (сверху вниз)
            row = ''
            for x in range(-size, size + 1):
                cell = self.BOARD.get((x, y), ' ')
                symbol = {
                    'start': 'S',
                    'gold': 'G',
                    'stone': '#',
                    ' ': '.'
                }.get(cell, '?')
                row += f'{symbol} '
            print(row)
