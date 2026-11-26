"""
Contacts model - WhatsApp-style contacts
"""
from django.db import models
import uuid


class Contact(models.Model):
    """User's contact list"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='contacts')
    contact_user = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='contacted_by')
    contact_name = models.CharField(max_length=100, blank=True)  # Custom name
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'contacts'
        unique_together = ['user', 'contact_user']
        ordering = ['contact_name', 'contact_user__full_name']
    
    def __str__(self):
        return f"{self.user.phone_number} -> {self.contact_user.phone_number}"
    
    @property
    def display_name(self):
        """Return custom name or user's full name"""
        return self.contact_name or self.contact_user.full_name or str(self.contact_user.phone_number)
