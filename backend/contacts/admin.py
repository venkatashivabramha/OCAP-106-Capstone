"""
Admin configuration for contacts
"""
from django.contrib import admin
from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['user', 'contact_user', 'contact_name', 'added_at']
    search_fields = ['user__phone_number', 'contact_user__phone_number', 'contact_name']
    list_filter = ['added_at']
    readonly_fields = ['id', 'added_at']
