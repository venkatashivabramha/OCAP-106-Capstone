"""
Admin configuration for messages
"""
from django.contrib import admin
from .models import Message, MessageStatus


class MessageStatusInline(admin.TabularInline):
    model = MessageStatus
    extra = 0
    readonly_fields = ['id', 'status_timestamp']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'conversation', 'message_type', 'created_at']
    list_filter = ['message_type', 'created_at']
    search_fields = ['text_content', 'sign_label', 'sender__phone_number']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [MessageStatusInline]


@admin.register(MessageStatus)
class MessageStatusAdmin(admin.ModelAdmin):
    list_display = ['message', 'user', 'status', 'status_timestamp']
    list_filter = ['status', 'status_timestamp']
    readonly_fields = ['id', 'status_timestamp']
