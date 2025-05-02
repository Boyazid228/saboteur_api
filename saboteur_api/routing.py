from django.urls import path
from game.consumers import LobbyConsumer
from django.urls import re_path

# path("ws/somepath/", MyConsumer.as_asgi()),
websocket_urlpatterns = [
    re_path(r'ws/lobby/(?P<lobby_id>\w+)/$', LobbyConsumer.as_asgi()),
]
