"""
Admin configuration for authentication
"""
from django.contrib import admin
from .models import User, UserProfile, OTP


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'full_name', 'is_online', 'created_at']
    search_fields = ['phone_number', 'full_name']
    list_filter = ['is_online', 'created_at']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_seen']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'display_name', 'is_online', 'created_at']
    search_fields = ['phone_number', 'display_name', 'user__username']
    list_filter = ['is_online', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'last_seen']


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'otp_code', 'is_verified', 'created_at', 'expires_at']
    search_fields = ['phone_number']
    list_filter = ['is_verified', 'created_at']
    readonly_fields = ['id', 'created_at']
