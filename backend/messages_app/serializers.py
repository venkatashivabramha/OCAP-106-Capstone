"""
Message serializers
"""
from rest_framework import serializers
from .models import Message, MessageStatus
from authentication.serializers import UserSerializer


class MessageStatusSerializer(serializers.ModelSerializer):
    """Message status serializer"""
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = MessageStatus
        fields = ['id', 'user', 'user_details', 'status', 'status_timestamp']
        read_only_fields = ['id', 'status_timestamp']


class MessageSerializer(serializers.ModelSerializer):
    """Message serializer"""
    sender_details = UserSerializer(source='sender', read_only=True)
    statuses = MessageStatusSerializer(many=True, read_only=True)
    reply_to_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'sender', 'sender_details',
            'message_type', 'text_content', 'sign_label', 'confidence_score',
            'media_url', 'reply_to_message', 'reply_to_details',
            'created_at', 'updated_at', 'statuses'
        ]
        read_only_fields = ['id', 'sender', 'created_at', 'updated_at']
    
    def get_reply_to_details(self, obj):
        if obj.reply_to_message:
            return {
                'id': obj.reply_to_message.id,
                'sender_name': obj.reply_to_message.sender.full_name,
                'text_content': obj.reply_to_message.text_content,
                'sign_label': obj.reply_to_message.sign_label
            }
        return None


class SendMessageSerializer(serializers.Serializer):
    """Send new message"""
    conversation_id = serializers.UUIDField()
    message_type = serializers.ChoiceField(choices=['text', 'sign', 'audio'])
    text_content = serializers.CharField(required=False, allow_blank=True)
    sign_label = serializers.CharField(max_length=50, required=False, allow_blank=True)
    confidence_score = serializers.FloatField(required=False)
    media_url = serializers.URLField(required=False, allow_blank=True)
    reply_to_message_id = serializers.UUIDField(required=False)


class UpdateMessageStatusSerializer(serializers.Serializer):
    """Update message read status"""
    message_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1
    )
    status = serializers.ChoiceField(choices=['delivered', 'read'])
