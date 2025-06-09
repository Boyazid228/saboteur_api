class Player:
    def __init__(self, id):
        self._id = id
        self._is_ready = False
        self._gold_cars = []
        self._cards = []
        self._status = 'Normal'
        self._player_card = None
        self._see_card = None

        self.pickaxe = True
        self.lantern = True
        self.cart = True

    @property
    def id(self):
        return self._id

    @property
    def is_ready(self):
        return self._is_ready

    @is_ready.setter
    def is_ready(self, value):
        if not isinstance(value, bool):
            raise ValueError("is_ready должен быть bool")
        self._is_ready = value

    @property
    def gold_cars(self):
        return self._gold_cars

    @gold_cars.setter
    def gold_cars(self, value):
        if not isinstance(value, list):
            raise ValueError("gold_cars должен быть list")
        self._gold_cars = value

    @property
    def cards(self):
        return self._cards

    @cards.setter
    def cards(self, value):
        if not isinstance(value, list):
            raise ValueError("cards должен быть list")
        self._cards = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if value not in ['Normal', 'Blocked']:
            raise ValueError("Неверный статус")
        self._status = value

    @property
    def player_card(self):
        return self._player_card

    @player_card.setter
    def player_card(self, value):
        self._player_card = value

    @property
    def see_card(self):
        return self._see_card

    @see_card.setter
    def see_card(self, value):
        self._see_card = value

    def get_player_json(self):
        return {
            'id': self.id,
            'pickaxe': self.pickaxe,
            'lantern': self.lantern,
            'cart': self.cart

        }

    def check_status(self):
        self.status = 'Normal' if self.cart and self.pickaxe and self.lantern else 'Blocked'

    def remove_card(self, rm_card):
        for index, card in enumerate(self._cards):
            if card.id == rm_card.id:
                self._cards.pop(index)
                return True
        return False
