"""
Admin configuration for typing indicators
"""
from django.contrib import admin
from .models import TypingIndicator


@admin.register(TypingIndicator)
class TypingIndicatorAdmin(admin.ModelAdmin):
    list_display = ['user', 'conversation', 'is_typing', 'updated_at']
    list_filter = ['is_typing', 'updated_at']
    readonly_fields = ['updated_at']
