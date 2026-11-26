"""
Conversations and participants models
"""
from django.db import models
import uuid


class Conversation(models.Model):
    is_group = models.BooleanField(default=False)
    group_name = models.CharField(max_length=100, blank=True, null=True)
    group_photo = models.ImageField(upload_to='group_photos/', blank=True, null=True)
    created_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True, related_name='created_groups')
    """Conversation (direct or group chat)"""
    CONVERSATION_TYPES = [
        ('direct', 'Direct'),
        ('group', 'Group'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation_type = models.CharField(max_length=10, choices=CONVERSATION_TYPES, default='direct')
    group_name = models.CharField(max_length=100, blank=True)
    group_picture_url = models.URLField(blank=True, null=True)
    created_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True)
    last_message_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'conversations'
        ordering = ['-last_message_at', '-created_at']
    
    def __str__(self):
        if self.conversation_type == 'group':
            return f"Group: {self.group_name}"
        return f"Direct conversation {self.id}"


class Participant(models.Model):
    """Participant in a conversation"""
    ROLES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'participants'
        unique_together = ['conversation', 'user']
        ordering = ['joined_at']
    
    def __str__(self):
        return f"{self.user.phone_number} in {self.conversation.id}"

