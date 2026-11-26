"""
Conversation views
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone

from authentication.models import User
from .models import Conversation, Participant
from .serializers import ConversationSerializer, CreateConversationSerializer


class ConversationListView(APIView):
    """List all conversations for user"""
    
    def get(self, request):
        # Get all conversations where user is a participant
        participant_conversations = Participant.objects.filter(
            user=request.user,
            left_at__isnull=True
        ).values_list('conversation_id', flat=True)
        
        conversations = Conversation.objects.filter(
            id__in=participant_conversations
        ).order_by('-last_message_at', '-created_at')
        
        serializer = ConversationSerializer(
            conversations, 
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
    
    def post(self, request):
        """Create new conversation"""
        serializer = CreateConversationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        conversation_type = serializer.validated_data['conversation_type']
        participant_ids = serializer.validated_data['participant_ids']
        group_name = serializer.validated_data.get('group_name', '')
        group_picture_url = serializer.validated_data.get('group_picture_url', '')
        
        # For direct conversations, check if already exists
        if conversation_type == 'direct':
            if len(participant_ids) != 1:
                return Response(
                    {'error': 'Direct conversation requires exactly 1 other participant'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if conversation already exists
            other_user_id = participant_ids[0]
            existing = Conversation.objects.filter(
                conversation_type='direct',
                participants__user=request.user,
                participants__left_at__isnull=True
            ).filter(
                participants__user_id=other_user_id,
                participants__left_at__isnull=True
            ).distinct().first()
            
            if existing:
                return Response(
                    ConversationSerializer(existing, context={'request': request}).data
                )
        
        # Create conversation
        conversation = Conversation.objects.create(
            conversation_type=conversation_type,
            group_name=group_name if conversation_type == 'group' else '',
            group_picture_url=group_picture_url if conversation_type == 'group' else '',
            created_by=request.user
        )
        
        # Add creator as participant
        Participant.objects.create(
            conversation=conversation,
            user=request.user,
            role='admin' if conversation_type == 'group' else 'member'
        )
        
        # Add other participants
        for user_id in participant_ids:
            try:
                user = User.objects.get(id=user_id)
                Participant.objects.create(
                    conversation=conversation,
                    user=user,
                    role='member'
                )
            except User.DoesNotExist:
                pass
        
        return Response(
            ConversationSerializer(conversation, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


class ConversationDetailView(APIView):
    """Get, update, or delete a conversation"""
    
    def get_object(self, request, conversation_id):
        try:
            # Check if user is participant
            participant = Participant.objects.get(
                conversation_id=conversation_id,
                user=request.user,
                left_at__isnull=True
            )
            return participant.conversation
        except Participant.DoesNotExist:
            return None
    
    def get(self, request, conversation_id):
        conversation = self.get_object(request, conversation_id)
        if not conversation:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ConversationSerializer(conversation, context={'request': request})
        return Response(serializer.data)
    
    def patch(self, request, conversation_id):
        """Update group name/picture"""
        conversation = self.get_object(request, conversation_id)
        if not conversation:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if conversation.conversation_type != 'group':
            return Response(
                {'error': 'Can only update group conversations'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is admin
        participant = Participant.objects.get(
            conversation=conversation,
            user=request.user
        )
        if participant.role != 'admin':
            return Response(
                {'error': 'Only admins can update group details'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        group_name = request.data.get('group_name')
        group_picture_url = request.data.get('group_picture_url')
        
        if group_name is not None:
            conversation.group_name = group_name
        if group_picture_url is not None:
            conversation.group_picture_url = group_picture_url
        
        conversation.save()
        
        return Response(ConversationSerializer(conversation, context={'request': request}).data)
    
    def delete(self, request, conversation_id):
        """Leave conversation"""
        conversation = self.get_object(request, conversation_id)
        if not conversation:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Mark participant as left
        participant = Participant.objects.get(
            conversation=conversation,
            user=request.user
        )
        participant.left_at = timezone.now()
        participant.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddParticipantsView(APIView):
    """Add participants to group"""
    
    def post(self, request, conversation_id):
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if conversation.conversation_type != 'group':
            return Response(
                {'error': 'Can only add participants to groups'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is admin
        try:
            participant = Participant.objects.get(
                conversation=conversation,
                user=request.user,
                left_at__isnull=True
            )
            if participant.role != 'admin':
                return Response(
                    {'error': 'Only admins can add participants'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Participant.DoesNotExist:
            return Response(
                {'error': 'Not a participant'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_ids = request.data.get('user_ids', [])
        added = []
        
        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                participant, created = Participant.objects.get_or_create(
                    conversation=conversation,
                    user=user,
                    defaults={'role': 'member'}
                )
                if created:
                    added.append(user_id)
            except User.DoesNotExist:
                pass
        
        return Response({
            'message': f'Added {len(added)} participants',
            'added_user_ids': added
        })


class RemoveParticipantView(APIView):
    """Remove participant from group"""
    
    def delete(self, request, conversation_id, user_id):
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if conversation.conversation_type != 'group':
            return Response(
                {'error': 'Can only remove participants from groups'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is admin
        try:
            admin_participant = Participant.objects.get(
                conversation=conversation,
                user=request.user,
                left_at__isnull=True
            )
            if admin_participant.role != 'admin':
                return Response(
                    {'error': 'Only admins can remove participants'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Participant.DoesNotExist:
            return Response(
                {'error': 'Not a participant'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Remove participant
        try:
            participant = Participant.objects.get(
                conversation=conversation,
                user_id=user_id
            )
            participant.left_at = timezone.now()
            participant.save()
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Participant.DoesNotExist:
            return Response(
                {'error': 'Participant not found'},
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['POST'])
def create_group(request):
    """Create a group conversation with multiple participants"""
    try:
        group_name = request.data.get('group_name')
        participant_ids = request.data.get('participant_ids', [])
        
        if not group_name:
            return Response({'error': 'Group name is required'}, status=400)
        
        if len(participant_ids) < 2:
            return Response({'error': 'At least 2 participants required'}, status=400)
        
        # Create group conversation
        conversation = Conversation.objects.create(
            is_group=True,
            group_name=group_name,
            created_by=request.user
        )
        
        # Add creator as participant
        Participant.objects.create(
            conversation=conversation,
            user=request.user,
            is_admin=True
        )
        
        # Add other participants
        for user_id in participant_ids:
            try:
                user = User.objects.get(id=user_id)
                Participant.objects.create(
                    conversation=conversation,
                    user=user
                )
            except User.DoesNotExist:
                pass
        
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data, status=201)
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def add_group_member(request, conversation_id):
    """Add a member to a group conversation"""
    try:
        conversation = Conversation.objects.get(id=conversation_id, is_group=True)
        
        # Check if requester is admin
        participant = Participant.objects.get(conversation=conversation, user=request.user)
        if not participant.is_admin:
            return Response({'error': 'Only admins can add members'}, status=403)
        
        user_id = request.data.get('user_id')
        user = User.objects.get(id=user_id)
        
        # Check if already a member
        if Participant.objects.filter(conversation=conversation, user=user).exists():
            return Response({'error': 'User is already a member'}, status=400)
        
        Participant.objects.create(conversation=conversation, user=user)
        
        return Response({'message': 'Member added successfully'}, status=200)
        
    except Conversation.DoesNotExist:
        return Response({'error': 'Group not found'}, status=404)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

