from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Conversation, Participant
from .serializers import ConversationSerializer
import uuid

User = get_user_model()


class ConversationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conv_ids = Participant.objects.filter(
            user=request.user, left_at__isnull=True
        ).values_list('conversation_id', flat=True)
        convs = Conversation.objects.filter(id__in=conv_ids).order_by('-last_message_at','-created_at')
        return Response(ConversationSerializer(convs, many=True, context={'request':request}).data)

    def post(self, request):
        phone_numbers = request.data.get('participant_phone_numbers', [])
        is_group = request.data.get('is_group', False)
        group_name = request.data.get('group_name', '')

        # Resolve phone numbers to User objects
        participants = []
        for phone in phone_numbers:
            try:
                u = User.objects.get(username=phone)
                participants.append(u)
            except User.DoesNotExist:
                pass

        if not is_group and len(participants) == 1:
            # Check for existing direct conversation
            existing = Conversation.objects.filter(
                conversation_type='direct',
                participants__user=request.user,
                participants__left_at__isnull=True
            ).filter(
                participants__user=participants[0],
                participants__left_at__isnull=True
            ).distinct().first()
            if existing:
                return Response(ConversationSerializer(existing, context={'request':request}).data)

        conv = Conversation.objects.create(
            conversation_type='group' if is_group else 'direct',
            group_name=group_name if is_group else '',
            created_by=request.user
        )
        Participant.objects.create(conversation=conv, user=request.user,
                                    role='admin' if is_group else 'member')
        for u in participants:
            Participant.objects.create(conversation=conv, user=u, role='member')

        return Response(ConversationSerializer(conv, context={'request':request}).data, status=201)


class ConversationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get(self, request, cid):
        try:
            p = Participant.objects.get(conversation_id=cid, user=request.user, left_at__isnull=True)
            return p.conversation
        except Participant.DoesNotExist:
            return None

    def get(self, request, conversation_id):
        c = self._get(request, conversation_id)
        if not c: return Response({'error':'Not found'}, status=404)
        return Response(ConversationSerializer(c, context={'request':request}).data)

    def delete(self, request, conversation_id):
        c = self._get(request, conversation_id)
        if not c: return Response({'error':'Not found'}, status=404)
        p = Participant.objects.get(conversation=c, user=request.user)
        p.left_at = timezone.now(); p.save()
        return Response(status=204)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_group(request):
    name = request.data.get('group_name','')
    ids  = request.data.get('participant_ids', [])
    if not name: return Response({'error':'group_name required'}, status=400)
    conv = Conversation.objects.create(conversation_type='group', group_name=name, created_by=request.user)
    Participant.objects.create(conversation=conv, user=request.user, role='admin')
    for uid in ids:
        try:
            u = User.objects.get(id=uid)
            Participant.objects.create(conversation=conv, user=u, role='member')
        except User.DoesNotExist:
            pass
    return Response(ConversationSerializer(conv, context={'request':request}).data, status=201)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_group_member(request, conversation_id):
    try:
        conv = Conversation.objects.get(id=conversation_id)
        p    = Participant.objects.get(conversation=conv, user=request.user, left_at__isnull=True)
        if p.role != 'admin': return Response({'error':'Admins only'}, status=403)
        uid = request.data.get('user_id')
        u   = User.objects.get(id=uid)
        Participant.objects.get_or_create(conversation=conv, user=u, defaults={'role':'member'})
        return Response({'message':'Added'})
    except Exception as e:
        return Response({'error':str(e)}, status=400)
