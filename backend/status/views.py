"""
User online/offline status views
"""
from rest_framework import status as http_status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone


class UpdateOnlineStatusView(APIView):
    """Update user's online/offline status"""
    
    def patch(self, request):
        is_online = request.data.get('is_online', True)
        
        request.user.is_online = is_online
        if not is_online:
            request.user.last_seen = timezone.now()
        request.user.save()
        
        return Response({
            'is_online': request.user.is_online,
            'last_seen': request.user.last_seen
        })
