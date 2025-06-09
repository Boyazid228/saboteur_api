from channels.generic.websocket import AsyncWebsocketConsumer
import json

from game.card import Card
from game.lobby import Lobby
from game.player import Player
from game.game import Game

active_lobbies = {}
active_games = {}


class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.lobby_id = self.scope['url_route']['kwargs']['lobby_id']
        self.player_id = self.channel_name
        self.player = Player(self.player_id)

        if self.lobby_id not in active_lobbies:
            active_lobbies[self.lobby_id] = Lobby(self.lobby_id)

        lobby = active_lobbies[self.lobby_id]
        added = lobby.add_player(self.player)

        await self.accept()

        if not added:
            await self.send(text_data=json.dumps({
                "message": "Lobby is full, sorry!",
                'player': 'system',
                'status': 'full'

            }))
            await self.close()
            return

        self.lobby_group_name = f'lobby_{self.lobby_id}'

        await self.channel_layer.group_add(self.lobby_group_name, self.channel_name)

        await self.channel_layer.group_send(
            self.lobby_group_name,
            {
                'type': 'chat.message',
                'message': f'Player {self.player.id} joined the lobby.',
                'player': 'system',
                'status': 'sys'
            }
        )

        players_json = [players.get_player_json() for players in lobby.get_players()]
        await self.channel_layer.group_send(
            self.lobby_group_name,
            {
                'type': 'chat.message',
                'message': players_json,
                'player': 'system',
                'status': 'join'
            }
        )

        await self.channel_layer.send(
            self.player.id,
            {
                'type': 'personal.message',
                'message': f'{self.player.id}',
                'player': 'system',
                'status': 'id'
            }
        )

        if lobby.is_full():
            active_games[self.lobby_id] = Game(lobby)
            await self.channel_layer.group_send(
                self.lobby_group_name,
                {
                    'type': 'chat.message',
                    'message': 'Full Lobby!',
                    'player': 'system',
                    'status': 'full_lobby',
                }
            )

    async def disconnect(self, close_code):
        lobby = active_lobbies.get(self.lobby_id)
        if lobby:
            lobby.remove_player(self.player.id)
            if not lobby.get_players():
                del active_lobbies[self.lobby_id]
                if self.lobby_id in active_games:
                    del active_games[self.lobby_id]

        if hasattr(self, 'lobby_group_name'):
            await self.channel_layer.group_discard(self.lobby_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        lobby = active_lobbies.get(self.lobby_id)

        if message == 'Ready':
            self.player.is_ready = True
            await self.send(text_data=json.dumps({
                'message': 'You have marked yourself as ready. Please wait for other players...',
                'player': 'system',
                'status': 'waiting'
            }))

            if lobby and lobby.is_ready():
                g = active_games.get(self.lobby_id)
                if g:
                    g.start()

                    cur_player = g.current_player()

                    for p in g.players:
                        cards_json = [card.get_json() for card in p.cards]
                        await self.channel_layer.send(
                            p.id,
                            {
                                'type': 'personal.message',
                                'message': cards_json,
                                'player': 'system',
                                'status': 'player_cards'
                            }
                        )

                        players_json = [players.get_player_json() for players in g.get_opponents(p.id)]
                        await self.channel_layer.send(
                            p.id,
                            {
                                'type': 'personal.message',
                                'message': players_json,
                                'player': 'system',
                                'status': 'players'
                            }
                        )

                    await self.channel_layer.group_send(
                        self.lobby_group_name,
                        {
                            'type': 'chat.message',
                            'message': 'All players are ready! The game begins!',
                            'player': 'system',
                            'status': 'start_game'
                        }
                    )

                    await self.channel_layer.group_send(
                        self.lobby_group_name,
                        {
                            'type': 'chat.message',
                            'message': g.board.get_board(),
                            'player': 'system',
                            'status': 'board'
                        }
                    )

                    await self.channel_layer.group_send(
                        self.lobby_group_name,
                        {
                            'type': 'chat.message',
                            'message': cur_player.id,
                            'player': 'system',
                            'status': 'play'
                        }
                    )

            else:
                await self.channel_layer.group_send(
                    self.lobby_group_name,
                    {
                            'type': 'chat.message',
                            'message': f'{self.player.id} ready',
                            'player': 'system',
                            'status': 'labby_player_ready',
                    }
                )

        elif data.get('action') == 'turn':

            if lobby and lobby.is_ready():
                g = active_games.get(self.lobby_id)
                if g:
                    if g.current_player().id == self.player.id:
                        if g.is_valid_move(self.player.id, data.get('message')):
                            if g.finish:
                                g.winner = g.current_player()
                                await self.channel_layer.group_send(
                                    self.lobby_group_name,
                                    {
                                        'type': 'chat.message',
                                        'message': g.current_player().id,
                                        'player': 'system',
                                        'status': 'winner'
                                    }
                                )
                                await self.channel_layer.group_send(
                                    self.lobby_group_name,
                                    {
                                        'type': 'chat.message',
                                        'message': g.board.get_board(),
                                        'player': 'system',
                                        'status': 'board'
                                    }
                                )

                                while True:
                                    cur_player = g.current_player()
                                    card_data = json.loads(cur_player.player_card.card_data)
                                    if card_data["player"] == "player":
                                        break
                                    else:
                                        g.next_turn()

                                await self.channel_layer.group_send(
                                    self.lobby_group_name,
                                    {
                                        'type': 'chat.message',
                                        'message': cur_player.id,
                                        'player': 'system',
                                        'status': 'play'
                                    }
                                )
                                await self.channel_layer.send(
                                    cur_player.id,
                                    {
                                        'type': 'personal.message',
                                        'message': g.dealer.get_gold_cards(),
                                        'player': 'system',
                                        'status': 'gold_cards'
                                    }
                                )

                                return True
                            if g.current_player().see_card is not None:
                                await self.channel_layer.send(
                                    self.player.id,
                                    {
                                        'type': 'personal.message',
                                        'message': g.current_player().see_card.get_json(),
                                        'player': 'system',
                                        'status': 'see_card'
                                    }
                                )
                                g.current_player().see_card = None

                            await self.channel_layer.send(
                                self.player.id,
                                {
                                    'type': 'personal.message',
                                    'message': 'Nice Turn',
                                    'player': 'system',
                                    'status': 'correct'
                                }
                            )
                            cards_json = [card.get_json() for card in self.player.cards]
                            await self.channel_layer.send(
                                self.player.id,
                                {
                                    'type': 'personal.message',
                                    'message': cards_json,
                                    'player': 'system',
                                    'status': 'player_cards'
                                }
                            )
                            g.next_turn()
                            cur_player = g.current_player()
                            await self.channel_layer.group_send(
                                self.lobby_group_name,
                                {
                                    'type': 'chat.message',
                                    'message': cur_player.id,
                                    'player': 'system',
                                    'status': 'play'
                                }
                            )

                            await self.channel_layer.group_send(
                                self.lobby_group_name,
                                {
                                    'type': 'chat.message',
                                    'message': g.board.get_board(),
                                    'player': 'system',
                                    'status': 'board'
                                }
                            )
                            await self.channel_layer.group_send(
                                self.lobby_group_name,
                                {
                                    'type': 'chat.message',
                                    'message': g.get_allowed_coords(),
                                    'player': 'system',
                                    'status': 'allowedCoords'
                                }
                            )

                            if g.last_action_player is not None:
                                await self.channel_layer.group_send(
                                    self.lobby_group_name,
                                    {
                                        'type': 'chat.message',
                                        'message': g.last_action_player.get_player_json(),
                                        'player': 'system',
                                        'status': 'update_player'
                                    }
                                )
                                g.last_action_player = None

                        else:
                            await self.channel_layer.send(
                                self.player.id,
                                {
                                    'type': 'personal.message',
                                    'message': g.board.get_board(),
                                    'player': 'system',
                                    'status': 'error_turn'
                                }
                            )

                            await self.channel_layer.send(
                                self.player.id,
                                {
                                    'type': 'personal.message',
                                    'message': self.player.get_player_json(),
                                    'player': 'system',
                                    'status': 'error'
                                }
                            )

                    else:
                        await self.channel_layer.send(
                            self.player.id,
                            {
                                'type': 'personal.message',
                                'message': 'Pleas wait!',
                                'player': 'system',
                                'status': 'waiting'
                            }
                        )
        elif data.get('action') == 'rotation' or data.get('action') == 'gold':
            if lobby and lobby.is_ready():
                g = active_games.get(self.lobby_id)
                if g:
                    message = json.loads(data.get('message'))
                    if data.get('action') == 'rotation':
                        card = g.check_card(message['card']['id'], message['player'])
                        if isinstance(card, Card):
                            card.is_rotated = not card.is_rotated
                    else:
                        if g.current_player().id == self.player.id:
                            g.set_gold_card(message['gold'], message['player'])

                            while True:
                                g.next_turn()
                                cur_player = g.current_player()
                                card_data = json.loads(cur_player.player_card.card_data)
                                if card_data["player"] == "player":
                                    break

                            await self.channel_layer.group_send(
                                self.lobby_group_name,
                                {
                                    'type': 'chat.message',
                                    'message': cur_player.id,
                                    'player': 'system',
                                    'status': 'play'
                                }
                            )
                            if len(g.dealer.gold_cards_for_players):
                                await self.channel_layer.send(
                                    cur_player.id,
                                    {
                                        'type': 'personal.message',
                                        'message': g.dealer.gold_cards_for_players,
                                        'player': 'system',
                                        'status': 'gold_cards'
                                    }
                                )
                            else:
                                p = g.winner_gold()
                                print(p)
                                await self.channel_layer.group_send(
                                    self.lobby_group_name,
                                    {
                                        'type': 'chat.message',
                                        'message': p,
                                        'player': 'system',
                                        'status': 'game_over'
                                    }
                                )


        else:
            await self.channel_layer.group_send(
                self.lobby_group_name,
                {
                    'type': 'chat.message',
                    'message': message,
                    'player': self.player.id,
                    'status': 'none',
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'player': event['player'],
            'status': event['status']
        }))

    async def personal_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'player': event['player'],
            'status': event['status'],
        }))
