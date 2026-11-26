"""
Status URL patterns
"""
from django.urls import path
from .views import UpdateOnlineStatusView

urlpatterns = [
    path('online/', UpdateOnlineStatusView.as_view(), name='update-online-status'),
]
