
class Lobby:
    def __init__(self, lobby_id, max_players=3):
        self.lobby_id = lobby_id
        self.max_players = max_players
        self.players = []

    def add_player(self, player):
        if len(self.players) >= self.max_players:
            return False
        self.players.append(player)
        return True

    def remove_player(self, player_id):
        for p in self.players:
            if p.id == player_id:
                self.players.remove(p)
                break

    def get_players(self):
        return self.players

    def get_player(self, id):
        for i in self.players:
            if i.id == id:
                return i
        return False

    def is_full(self):
        return len(self.players) == self.max_players

    def is_ready(self):
        return all(p.is_ready for p in self.players)
