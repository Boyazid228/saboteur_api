from game.card import Card
import json


class Board:
    def __init__(self):
        self._board = {
            (0, 0): Card("start", 'path',
                         json.dumps({"img": "start.jpg", "type": "path", "matrix": [[0, 1, 0], [1, 1, 1], [0, 1, 0]],
                                     "gols": 0,
                                     "action": "",
                                     "player": "", "start": True, "finish": False})),
            (8, 2): Card("finish1", 'path',
                         json.dumps({"img": "stone.jpg", "type": "path", "matrix": [[0, 1, 0], [1, 1, 1], [0, 1, 0]],
                                     "gols": 0,
                                     "action": "",
                                     "player": "", "start": False, "finish": True})),
            (8, 0): Card("finish2", 'path',
                         json.dumps(
                             {"img": "gold.jpg", "type": "path", "matrix": [[0, 1, 0], [1, 1, 1], [0, 1, 0]], "gols": 1,
                              "action": "",
                              "player": "", "start": False, "finish": True})),
            (8, -2): Card("finish3", 'path',
                          json.dumps({"img": "stone.jpg", "type": "path", "matrix": [[0, 1, 0], [1, 1, 1], [0, 1, 0]],
                                      "gols": 0,
                                      "action": "",
                                      "player": "", "start": False, "finish": True})),
        }

        self.allowed_coords = {(0, 1), (1, 0), (-1, 0), (0, -1)}

    def to_json(self, board):
        return {
            f"{x},{y}": value.get_json()
            for (x, y), value in board.items()
        }

    def to_list(self):
        return [
            {"x": x, "y": y, "value": value.get_json()}
            for (x, y), value in self._board.items()
        ]

    def add_item(self, x, y, card):
        if (x, y) not in self._board:
            self._board[(x, y)] = card
            self.update_allowed_coords(x, y, card)
        return self._board

    def update_allowed_coords(self, x, y, card):
        coord = (x, y)
        self.allowed_coords.discard(coord)
        direction = [[-1, 0], [1, 0], [0, 1], [0, -1]]
        possible_path = [[1, 0], [1, 2], [2, 1], [0, 1]]
        matrix = json.loads(card.card_data)["matrix"]

        for index, i in enumerate(direction):
            if (x + i[0], y + i[1]) in self._board:
                continue

            px, py = possible_path[index]
            value = matrix[2 - px][2 - py] if card.is_rotated else matrix[px][py]

            if value:
                self.allowed_coords.add((x + i[0], y + i[1]))

    def get_board(self):
        temp = self._board
        temp[(8, 2)] = Card("hidden", 'path', json.dumps({
            "img": "hidden.jpg", "type": "path", "matrix": [],
            "gols": 0, "action": "", "player": "", "start": False, "finish": False
        }))
        temp[(8, 0)] = Card("hidden", 'path', json.dumps({
            "img": "hidden.jpg", "type": "path", "matrix": [],
            "gols": 0, "action": "", "player": "", "start": False, "finish": False
        }))
        temp[(8, -2)] = Card("hidden", 'path', json.dumps({
            "img": "hidden.jpg", "type": "path", "matrix": [],
            "gols": 0, "action": "", "player": "", "start": False, "finish": False
        }))
        return self.to_json(temp)

    def has_card_at(self, x, y):
        return (x, y) in self._board

    def get_card_at(self, x, y):
        return self._board.get((x, y))
    def show(self, size=9):
        # size — радиус сетки: от -size до +size
        for y in range(size, -1 - size, -1):  # от +size до -size (сверху вниз)
            row = ''
            for x in range(-size, size + 1):
                cell = self._board.get((x, y), ' ')
                symbol = {
                    'start': 'S',
                    'gold': 'G',
                    'stone': '#',
                    ' ': '.'
                }.get(cell, '?')
                row += f'{symbol} '
            print(row)
