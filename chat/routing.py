from django.urls import re_path, path
from .consumers import PersonalChatConsumer


websocket_urlpatterns = [
    # re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    path('ws/<int:id>/', PersonalChatConsumer.as_asgi()),
    path('wss/<int:id>/', PersonalChatConsumer.as_asgi())

]