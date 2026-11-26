from django.db import models
from django.conf import settings
import uuid

class Conversation(models.Model):
    TYPES = [('direct','Direct'),('group','Group')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation_type = models.CharField(max_length=10, choices=TYPES, default='direct')
    group_name = models.CharField(max_length=100, blank=True)
    group_picture_url = models.URLField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_conversations')
    last_message_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'conversations'
        ordering = ['-last_message_at','-created_at']
    def __str__(self):
        return f"{'Group: '+self.group_name if self.conversation_type=='group' else 'Direct '+str(self.id)}"

class Participant(models.Model):
    ROLES = [('admin','Admin'),('member','Member')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = 'participants'
        unique_together = ['conversation','user']
        ordering = ['joined_at']
