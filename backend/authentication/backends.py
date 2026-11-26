"""
JWT Authentication backend
"""
import jwt
from django.conf import settings
from rest_framework import authentication, exceptions
from .models import User


class JWTAuthentication(authentication.BaseAuthentication):
    """Custom JWT authentication"""
    
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return None
        
        try:
            # Extract token from "Bearer <token>"
            prefix, token = auth_header.split(' ')
            if prefix.lower() != 'bearer':
                return None
            
            # Decode JWT token
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # Get user from payload
            user_id = payload.get('user_id')
            if not user_id:
                raise exceptions.AuthenticationFailed('Invalid token')
            
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise exceptions.AuthenticationFailed('User not found')
            
            return (user, token)
            
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')
        except ValueError:
            raise exceptions.AuthenticationFailed('Invalid authorization header')
