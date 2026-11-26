"""
Message views
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone

from conversations.models import Conversation, Participant
from .models import Message, MessageStatus
from .serializers import (
    MessageSerializer, SendMessageSerializer, UpdateMessageStatusSerializer
)


class MessageListView(APIView):
    """Get messages for a conversation (paginated)"""
    
    def get(self, request):
        conversation_id = request.query_params.get('conversation_id')
        
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
        
        # Get messages (ordered newest first, but reversed for display)
        messages = Message.objects.filter(
            conversation_id=conversation_id
        ).select_related('sender', 'reply_to_message').prefetch_related('statuses')
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))
        start = (page - 1) * page_size
        end = start + page_size
        
        paginated_messages = messages[start:end]
        
        serializer = MessageSerializer(paginated_messages, many=True)
        
        return Response({
            'messages': serializer.data,
            'page': page,
            'page_size': page_size,
            'has_more': messages.count() > end
        })
    
    def post(self, request):
        """Send new message"""
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        conversation_id = serializer.validated_data['conversation_id']
        message_type = serializer.validated_data['message_type']
        text_content = serializer.validated_data.get('text_content', '')
        sign_label = serializer.validated_data.get('sign_label', '')
        confidence_score = serializer.validated_data.get('confidence_score')
        media_url = serializer.validated_data.get('media_url', '')
        reply_to_message_id = serializer.validated_data.get('reply_to_message_id')
        
        # Check if user is participant
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            Participant.objects.get(
                conversation=conversation,
                user=request.user,
                left_at__isnull=True
            )
        except (Conversation.DoesNotExist, Participant.DoesNotExist):
            return Response(
                {'error': 'Not a participant of this conversation'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get reply_to message if specified
        reply_to_message = None
        if reply_to_message_id:
            try:
                reply_to_message = Message.objects.get(id=reply_to_message_id)
            except Message.DoesNotExist:
                pass
        
        # Create message
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            message_type=message_type,
            text_content=text_content,
            sign_label=sign_label,
            confidence_score=confidence_score,
            media_url=media_url,
            reply_to_message=reply_to_message
        )
        
        # Update conversation's last_message_at
        conversation.last_message_at = message.created_at
        conversation.save()
        
        # Create message status for all participants (except sender)
        participants = Participant.objects.filter(
            conversation=conversation,
            left_at__isnull=True
        ).exclude(user=request.user)
        
        for participant in participants:
            MessageStatus.objects.create(
                message=message,
                user=participant.user,
                status='sent'
            )
        
        return Response(
            MessageSerializer(message).data,
            status=status.HTTP_201_CREATED
        )


class MessageDetailView(APIView):
    """Delete a message"""
    
    def delete(self, request, message_id):
        try:
            message = Message.objects.get(id=message_id, sender=request.user)
            message.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Message.DoesNotExist:
            return Response(
                {'error': 'Message not found or not authorized'},
                status=status.HTTP_404_NOT_FOUND
            )


class UpdateMessageStatusView(APIView):
    """Update message status (delivered/read)"""
    
    def patch(self, request):
        serializer = UpdateMessageStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        message_ids = serializer.validated_data['message_ids']
        new_status = serializer.validated_data['status']
        
        updated = 0
        for message_id in message_ids:
            try:
                message = Message.objects.get(id=message_id)
                
                # Check if user is participant
                Participant.objects.get(
                    conversation=message.conversation,
                    user=request.user,
                    left_at__isnull=True
                )
                
                # Update or create status
                message_status, created = MessageStatus.objects.get_or_create(
                    message=message,
                    user=request.user,
                    defaults={'status': new_status}
                )
                
                if not created:
                    message_status.status = new_status
                    message_status.save()
                
                updated += 1
                
            except (Message.DoesNotExist, Participant.DoesNotExist):
                continue
        
        return Response({
            'message': f'Updated {updated} message statuses',
            'updated_count': updated
        })
