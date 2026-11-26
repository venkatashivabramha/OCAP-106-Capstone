"""
Messages and message status models
"""
from django.db import models
import uuid


class Message(models.Model):
    """Message in a conversation"""
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('sign', 'Sign Language'),
        ('audio', 'Audio'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey('conversations.Conversation', on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    text_content = models.TextField(blank=True)
    sign_label = models.CharField(max_length=50, blank=True)  # Recognized sign
    confidence_score = models.FloatField(null=True, blank=True)  # AI confidence
    media_url = models.URLField(blank=True, null=True)  # Audio/video URL
    reply_to_message = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'messages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['conversation', '-created_at']),
            models.Index(fields=['sender']),
        ]
    
    def __str__(self):
        return f"Message from {self.sender.phone_number} in {self.conversation.id}"


class MessageStatus(models.Model):
    """Read receipt for messages"""
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='statuses')
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    status_timestamp = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'message_status'
        unique_together = ['message', 'user']
        ordering = ['-status_timestamp']
    
    def __str__(self):
        return f"{self.status} - {self.message.id} - {self.user.phone_number}"
