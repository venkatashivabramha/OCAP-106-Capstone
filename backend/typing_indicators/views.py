"""
Typing indicator views
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from conversations.models import Participant
from .models import TypingIndicator


class SetTypingIndicatorView(APIView):
    """Set typing indicator for a conversation"""
    
    def post(self, request):
        conversation_id = request.data.get('conversation_id')
        is_typing = request.data.get('is_typing', True)
        
        if not conversation_id:
            return Response(
                {'error': 'conversation_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is participant
        try:
            Participant.objects.get(
                conversation_id=conversation_id,
                user=request.user,
                left_at__isnull=True
            )
        except Participant.DoesNotExist:
            return Response(
                {'error': 'Not a participant of this conversation'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update or create typing indicator
        typing_indicator, created = TypingIndicator.objects.update_or_create(
            conversation_id=conversation_id,
            user=request.user,
            defaults={'is_typing': is_typing}
        )
        
        return Response({
            'conversation_id': conversation_id,
            'is_typing': is_typing,
            'user_id': str(request.user.id)
        })
