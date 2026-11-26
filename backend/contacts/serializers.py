"""
Contact serializers
"""
from rest_framework import serializers
from .models import Contact
from authentication.serializers import UserSerializer


class ContactSerializer(serializers.ModelSerializer):
    """Contact serializer with user details"""
    contact_user_details = UserSerializer(source='contact_user', read_only=True)
    display_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Contact
        fields = [
            'id', 'contact_user', 'contact_user_details', 
            'contact_name', 'display_name', 'added_at'
        ]
        read_only_fields = ['id', 'added_at']


class AddContactSerializer(serializers.Serializer):
    """Add contact by phone number"""
    phone_number = serializers.CharField(max_length=15)
    contact_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
