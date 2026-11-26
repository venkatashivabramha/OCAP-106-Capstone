from django.urls import path
from . import views
from .views import ConversationListView, ConversationDetailView

urlpatterns = [
    path('create-group/', views.create_group, name='create-group'),
    path('<uuid:conversation_id>/add-member/', views.add_group_member, name='add-group-member'),
    path('', ConversationListView.as_view(), name='conversation-list'),
    path('<uuid:conversation_id>/', ConversationDetailView.as_view(), name='conversation-detail'),
]
