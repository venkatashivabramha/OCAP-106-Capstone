"""
Conversation serializers
"""
from rest_framework import serializers
from .models import Conversation, Participant
from authentication.serializers import UserSerializer


class ParticipantSerializer(serializers.ModelSerializer):
    """Participant serializer"""
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Participant
        fields = ['id', 'user', 'user_details', 'role', 'joined_at', 'left_at']
        read_only_fields = ['id', 'joined_at']


class ConversationSerializer(serializers.ModelSerializer):
    """Conversation serializer with participants"""
    participants_list = ParticipantSerializer(source='participants', many=True, read_only=True)
    participant_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'conversation_type', 'group_name', 'group_picture_url',
            'created_by', 'last_message_at', 'created_at', 'updated_at',
            'participants_list', 'participant_count', 'last_message', 'unread_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_message_at']
    
    def get_participant_count(self, obj):
        return obj.participants.filter(left_at__isnull=True).count()
    
    def get_last_message(self, obj):
        # Import here to avoid circular import
        from messages_app.models import Message
        last_msg = Message.objects.filter(conversation=obj).first()
        if last_msg:
            return {
                'text_content': last_msg.text_content,
                'sign_label': last_msg.sign_label,
                'sender_name': last_msg.sender.full_name,
                'created_at': last_msg.created_at
            }
        return None
    
    def get_unread_count(self, obj):
        # Count unread messages for current user
        request = self.context.get('request')
        if not request or not request.user:
            return 0
        
        from messages_app.models import Message, MessageStatus
        messages = Message.objects.filter(conversation=obj).exclude(sender=request.user)
        unread = 0
        for msg in messages:
            status = MessageStatus.objects.filter(message=msg, user=request.user).first()
            if not status or status.status != 'read':
                unread += 1
        return unread


class CreateConversationSerializer(serializers.Serializer):
    """Create new conversation"""
    conversation_type = serializers.ChoiceField(choices=['direct', 'group'])
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1
    )
    group_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    group_picture_url = serializers.URLField(required=False, allow_blank=True)
