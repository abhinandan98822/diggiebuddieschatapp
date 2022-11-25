from django.urls import path
from . import views
urlpatterns = [
    path('chat/', views.private_chat_home, name='chat-index'),
    path('chat/<str:username>/', views.chatPage, name='chat-room'),
]