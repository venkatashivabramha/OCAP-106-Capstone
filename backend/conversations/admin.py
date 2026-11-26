"""
Admin configuration for conversations
"""
from django.contrib import admin
from .models import Conversation, Participant


class ParticipantInline(admin.TabularInline):
    model = Participant
    extra = 0
    readonly_fields = ['id', 'joined_at']


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation_type', 'group_name', 'created_by', 'created_at']
    list_filter = ['conversation_type', 'created_at']
    search_fields = ['group_name', 'id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [ParticipantInline]


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'conversation', 'role', 'joined_at', 'left_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['user__phone_number', 'conversation__id']
    readonly_fields = ['id', 'joined_at']
