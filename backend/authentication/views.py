
"""
Authentication Views with Firebase OTP
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .firebase_auth import firebase_service
from .models import UserProfile
from .serializers import UserProfileSerializer

User = get_user_model()

class SendOTPView(APIView):
    """
    Send OTP to mobile number
    POST /api/auth/send-otp/
    Body: {"phone_number": "+911234567890"}
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        phone_number = request.data.get('phone_number')
        
        if not phone_number:
            return Response({
                'error': 'Phone number is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate phone number format
        if not phone_number.startswith('+'):
            return Response({
                'error': 'Phone number must include country code (e.g., +91...)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Send OTP via Firebase
        result = firebase_service.send_otp(phone_number)
        
        if result['success']:
            response_data = {
                'message': result['message'],
                'phone_number': phone_number
            }
            
            # Include OTP in response ONLY for simulation mode
            if result.get('simulation'):
                response_data['otp'] = result['otp']
                response_data['note'] = 'Simulation mode: Use OTP 123456'
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Failed to send OTP'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyOTPView(APIView):
    """
    Verify OTP and create/login user
    POST /api/auth/verify-otp/
    Body: {
        "phone_number": "+911234567890",
        "otp": "123456"  # For simulation
        OR
        "id_token": "firebase_id_token"  # For production
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        phone_number = request.data.get('phone_number')
        otp = request.data.get('otp')
        id_token = request.data.get('id_token')
        
        if not phone_number:
            return Response({
                'error': 'Phone number is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify via Firebase ID token (production) or OTP (simulation)
        if id_token:
            result = firebase_service.verify_id_token(id_token)
        elif otp:
            result = firebase_service.verify_otp(phone_number, otp)
        else:
            return Response({
                'error': 'Either OTP or ID token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not result['success']:
            return Response({
                'error': result.get('error', 'Verification failed')
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get or create user
        firebase_uid = result['uid']
        verified_phone = result.get('phone_number', phone_number)
        
        # Create or get Django user
        user, created = User.objects.get_or_create(
            username=verified_phone,
            defaults={'email': f'{firebase_uid}@isl.app'}
        )
        
        # Create or get user profile
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'phone_number': verified_phone,
                'firebase_uid': firebase_uid
            }
        )
        
        # Update firebase_uid if needed
        if profile.firebase_uid != firebase_uid:
            profile.firebase_uid = firebase_uid
            profile.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Authentication successful',
            'user_id': user.id,
            'username': user.username,
            'phone_number': verified_phone,
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'is_new_user': created,
            'simulation': result.get('simulation', False)
        }, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """
    Get/Update user profile
    GET /api/auth/profile/
    PUT /api/auth/profile/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'Profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'Profile not found'
            }, status=status.HTTP_404_NOT_FOUND)


class LogoutView(APIView):
    """
    Logout user (blacklist refresh token)
    POST /api/auth/logout/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
