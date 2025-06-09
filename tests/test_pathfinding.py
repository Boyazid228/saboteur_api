import unittest
import json
from game.board import Board
from game.card import Card
from game.game import Game
from game.lobby import Lobby
from collections import deque


class TestPathFinding(unittest.TestCase):

    def setUp(self):


        cards = {
            (0, 0):  Card("start", 'path',
                         json.dumps({"img": "start.jpg", "type": "path", "matrix": [[0, 1, 0], [1, 1, 1], [0, 1, 0]],
                                     "gols": 0,
                                     "action": "",
                                     "player": "", "start": True, "finish": False})),
            (1, 0): Card("finish2", 'path',
                         json.dumps(
                             {"img": "gold.jpg", "type": "path", "matrix": [[0, 1, 0], [1, 1, 1], [0, 1, 0]], "gols": 1,
                              "action": "",
                              "player": "", "start": False, "finish": False})),
            (2, 0): Card("finish2", 'path',
                         json.dumps(
                             {"img": "gold.jpg", "type": "path", "matrix": [[0, 1, 0], [1, 1, 1], [0, 1, 0]], "gols": 1,
                              "action": "",
                              "player": "", "start": False, "finish": False})),
            (3, 0): Card("finish2", 'path',
                         json.dumps(
                             {"img": "gold.jpg", "type": "path", "matrix": [[0, 1, 0], [1, 1, 1], [0, 1, 0]], "gols": 1,
                              "action": "",
                              "player": "", "start": False, "finish": False})),
            (4, 0): Card("finish2", 'path',
                         json.dumps(
                             {"img": "gold.jpg", "type": "path", "matrix": [[0, 1, 0], [1, 1, 1], [0, 1, 0]], "gols": 1,
                              "action": "",
                              "player": "", "start": False, "finish": True})),
        }
        self.game = Game(Lobby("23"))

        self.board = self.game.board
        for (x, y), card in cards.items():
            self.game.add_item(x, y, card)

    def test_path_exists(self):
        path = self.game.find_path_a_star()
        print("Path found:", path)
        self.assertIsNotNone(path)
        self.assertEqual(path[0], (0, 0))
        self.assertIn((4, 0), path)

    def test_no_path(self):
        self.board.BOARD[(1, 0)] = Card("block", "path", json.dumps({
            "matrix": [
                [0, 0, 0],
                [0, 1, 0],
                [0, 0, 0]
            ],
            "start": False,
            "finish": False
        }))
        path = self.game.find_path_a_star()
        print("Path found:", path)
        self.assertIsNone(path)

if __name__ == '__main__':
    unittest.main()
