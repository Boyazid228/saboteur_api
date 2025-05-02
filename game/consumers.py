from channels.generic.websocket import AsyncWebsocketConsumer
import json
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
                "message": "Lobby is full, sorry!"
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
                'status': 'none'
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

        if message == 'Ready':
            self.player.is_ready = True
            await self.send(text_data=json.dumps({
                'message': 'Вы отметили себя как готового. Пожалуйста, подождите других игроков...',
                'player': 'system',
                'status': 'waiting'
            }))

            lobby = active_lobbies.get(self.lobby_id)
            if lobby and lobby.is_ready():
                g = active_games.get(self.lobby_id)
                if g:
                    g.start()

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

                    await self.channel_layer.group_send(
                        self.lobby_group_name,
                        {
                            'type': 'chat.message',
                            'message': 'Все игроки готовы! Игра начинается!',
                            'player': 'system',
                            'status': 'start_game'
                        }
                    )

                    await self.channel_layer.group_send(
                        self.lobby_group_name,
                        {
                            'type': 'chat.message',
                            'message': g.board.to_json(),
                            'player': 'system',
                            'status': 'board'
                        }
                    )

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

            else:
                await self.channel_layer.group_send(
                    self.lobby_group_name,
                    {
                            'type': 'chat.message',
                            'message': f'{self.player.id} ready',
                            'player': 'system',
                            'status': 'none',
                    }
                )

        elif data.get('action') == 'turn':

            lobby = active_lobbies.get(self.lobby_id)
            if lobby and lobby.is_ready():
                g = active_games.get(self.lobby_id)
                if g:
                    if g.current_player().id == self.player.id:
                        if g.is_valid_move(self.player.id, data.get('message')):
                            await self.channel_layer.send(
                                self.player.id,
                                {
                                    'type': 'personal.message',
                                    'message': 'Nice Turn',
                                    'player': 'system',
                                    'status': 'waiting'
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
                                    'message': g.board.to_json(),
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

                        else:
                            await self.channel_layer.send(
                                self.player.id,
                                {
                                    'type': 'personal.message',
                                    'message': 'Error Turn! do agin',
                                    'player': 'system',
                                    'status': 'turn'
                                }
                            )

                    else:
                        await self.channel_layer.send(
                            self.player.id,
                            {
                                'type': 'personal.message',
                                'message': 'Pleas Wait!!!',
                                'player': 'system',
                                'status': 'waiting'
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
