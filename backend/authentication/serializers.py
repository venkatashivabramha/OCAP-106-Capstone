"""
Serializers for authentication
"""
from rest_framework import serializers
from django.contrib.auth.models import User as DjangoUser
from .models import User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """UserProfile serializer for Firebase authenticated users"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'phone_number', 'display_name', 'bio',
            'avatar_url', 'is_online', 'last_seen', 'created_at'
        ]
        read_only_fields = ['id', 'username', 'phone_number', 'created_at', 'last_seen']


class UserSerializer(serializers.ModelSerializer):
    """Legacy User serializer"""
    phone_number = serializers.CharField()
    
    class Meta:
        model = User
        fields = [
            'id', 'phone_number', 'full_name', 'profile_picture_url',
            'about_text', 'is_online', 'last_seen', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_seen']


class SendOTPSerializer(serializers.Serializer):
    """Serializer for sending OTP"""
    phone_number = serializers.CharField(max_length=15)


class VerifyOTPSerializer(serializers.Serializer):
    """Serializer for verifying OTP and login/register"""
    phone_number = serializers.CharField(max_length=15)
    otp_code = serializers.CharField(max_length=6)
    full_name = serializers.CharField(max_length=100, required=False)
    password = serializers.CharField(write_only=True, required=False)


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    class Meta:
        model = User
        fields = ['full_name', 'profile_picture_url', 'about_text']


class TokenSerializer(serializers.Serializer):
    """Token response serializer"""
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    user = UserSerializer()
