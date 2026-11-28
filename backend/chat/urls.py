from django.urls import path
from . import views
urlpatterns = [
    path('join/', views.join, name='chat-join'),
    path('messages/', views.messages, name='chat-messages'),
    path('users/', views.users, name='chat-users'),
    path('send/', views.send_message, name='chat-send'),
]
