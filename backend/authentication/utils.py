"""
Utility functions for authentication
"""
import jwt
import random
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone


def generate_otp():
    """Generate 6-digit OTP"""
    return str(random.randint(100000, 999999))


def send_otp_sms(phone_number, otp_code):
    """
    Send OTP via SMS
    In production, integrate with Twilio, AWS SNS, or similar service
    For demo, just print to console
    """
    print(f"📱 Sending OTP to {phone_number}: {otp_code}")
    # TODO: Integrate with SMS provider
    # import boto3
    # sns = boto3.client('sns')
    # sns.publish(PhoneNumber=phone_number, Message=f"Your Signa Link OTP: {otp_code}")
    return True


def generate_jwt_tokens(user):
    """Generate access and refresh tokens"""
    
    # Access token (short-lived)
    access_payload = {
        'user_id': str(user.id),
        'phone_number': str(user.phone_number),
        'exp': datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        'iat': datetime.utcnow(),
        'type': 'access'
    }
    access_token = jwt.encode(
        access_payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    # Refresh token (long-lived)
    refresh_payload = {
        'user_id': str(user.id),
        'exp': datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        'iat': datetime.utcnow(),
        'type': 'refresh'
    }
    refresh_token = jwt.encode(
        refresh_payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }


def verify_refresh_token(token):
    """Verify and decode refresh token"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        if payload.get('type') != 'refresh':
            return None
        
        return payload.get('user_id')
        
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
