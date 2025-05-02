class Card:

    def __init__(self, id, type, card_data):
        self.type = type
        self.card_data = card_data
        self.is_rotated = False
        self.id = id

    def show(self):
        print(self.type, self.card_data, self.is_rotated)

    def get_json(self):
        return {
            'id': self.id,
            'type': self.type,
            'card_data': self.card_data,
            'is_rotated': self.is_rotated

        }

