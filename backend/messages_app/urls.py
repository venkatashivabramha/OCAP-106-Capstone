"""
Messages URL patterns
"""
from django.urls import path
from .views import MessageListView, MessageDetailView, UpdateMessageStatusView

urlpatterns = [
    path('', MessageListView.as_view(), name='message-list'),
    path('<uuid:message_id>/', MessageDetailView.as_view(), name='message-detail'),
    path('status/', UpdateMessageStatusView.as_view(), name='update-message-status'),
]
