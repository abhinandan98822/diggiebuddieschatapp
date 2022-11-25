# from django.urls import re_path
# from . import consumers

# websocket_urlpatterns = [
#     re_path(r'wss/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
#     re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
   
# ]

from django.urls import re_path, path
from mainapp.consumers import PersonalChatConsumer


websocket_urlpatterns = [
    # re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    path('ws/<int:id>/', PersonalChatConsumer.as_asgi()),
    path('wss/<int:id>/', PersonalChatConsumer.as_asgi())

]

