"""
Typing indicator URL patterns
"""
from django.urls import path
from .views import SetTypingIndicatorView

urlpatterns = [
    path('', SetTypingIndicatorView.as_view(), name='set-typing-indicator'),
]
