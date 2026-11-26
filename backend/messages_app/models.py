from django.db import models
from django.conf import settings
import uuid

class Message(models.Model):
    TYPES = [('text','Text'),('sign','Sign Language'),('audio','Audio')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey('conversations.Conversation', on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message_type = models.CharField(max_length=20, choices=TYPES, default='text')
    text_content = models.TextField(blank=True)
    sign_label = models.CharField(max_length=50, blank=True)
    confidence_score = models.FloatField(null=True, blank=True)
    media_url = models.URLField(blank=True, null=True)
    reply_to_message = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'messages'
        ordering = ['-created_at']

class MessageStatus(models.Model):
    STATUS = [('sent','Sent'),('delivered','Delivered'),('read','Read')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='statuses')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS, default='sent')
    status_timestamp = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'message_statuses'
        unique_together = ['message','user']
