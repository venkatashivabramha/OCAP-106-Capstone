"""
User models for Signa Link with Firebase authentication
"""
from django.db import models
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth.hashers import make_password, check_password
from phonenumber_field.modelfields import PhoneNumberField
import uuid


class User(models.Model):
    """Legacy user model for Signa Link - WhatsApp-style authentication"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = PhoneNumberField(unique=True, region='IN')
    password_hash = models.CharField(max_length=255)
    full_name = models.CharField(max_length=100, blank=True)
    profile_picture_url = models.URLField(blank=True, null=True)
    about_text = models.CharField(
        max_length=255, 
        default='Hey there! I am using Signa Link'
    )
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name or 'User'} ({self.phone_number})"
    
    @property
    def is_authenticated(self):
        """Always return True for authenticated users"""
        return True
    
    @property
    def is_anonymous(self):
        """Always return False - this is a real user"""
        return False
    
    def set_password(self, raw_password):
        """Hash and set password"""
        self.password_hash = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Verify password"""
        return check_password(raw_password, self.password_hash)


class UserProfile(models.Model):
    """Extended profile for Django auth users (Firebase authentication)"""
    user = models.OneToOneField(DjangoUser, on_delete=models.CASCADE, related_name='isl_profile')
    phone_number = PhoneNumberField(unique=True, region='IN')
    firebase_uid = models.CharField(max_length=128, unique=True, null=True, blank=True)
    display_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar_url = models.URLField(blank=True, null=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.display_name or self.user.username} ({self.phone_number})"


class OTP(models.Model):
    """OTP model for mobile number verification"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = PhoneNumberField(region='IN')
    otp_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'otps'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OTP for {self.phone_number} - {self.otp_code}"
    
    def is_valid(self):
        """Check if OTP is still valid"""
        from django.utils import timezone
        return not self.is_verified and self.expires_at > timezone.now()
