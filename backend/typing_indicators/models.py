"""
Typing indicators model
"""
from django.db import models
import uuid


class TypingIndicator(models.Model):
    """Track typing indicators for conversations"""
    conversation = models.ForeignKey('conversations.Conversation', on_delete=models.CASCADE)
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    is_typing = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'typing_indicators'
        unique_together = ['conversation', 'user']
    
    def __str__(self):
        return f"{self.user.phone_number} typing in {self.conversation.id}"
