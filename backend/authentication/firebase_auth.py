
"""
Firebase Authentication Service for Mobile OTP
"""
import firebase_admin
from firebase_admin import credentials, auth
from django.conf import settings
import os
import json

class FirebaseAuthService:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseAuthService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialize_firebase()
            self._initialized = True
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Try to get service account from environment
            service_account_path = getattr(settings, 'FIREBASE_SERVICE_ACCOUNT_KEY', None)
            
            if service_account_path and os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
            else:
                # Use default credentials or service account from settings
                service_account_dict = getattr(settings, 'FIREBASE_SERVICE_ACCOUNT_DICT', None)
                if service_account_dict:
                    cred = credentials.Certificate(service_account_dict)
                else:
                    print("Warning: Firebase credentials not configured. Using simulation mode.")
                    self.simulation_mode = True
                    return
            
            firebase_admin.initialize_app(cred)
            self.simulation_mode = False
            print("? Firebase Admin SDK initialized")
            
        except Exception as e:
            print(f"Firebase initialization failed: {e}")
            print("Running in simulation mode")
            self.simulation_mode = True
    
    def send_otp(self, phone_number):
        """
        Send OTP to phone number
        In production, Firebase handles OTP via client SDK
        Server only verifies the ID token
        """
        if self.simulation_mode:
            # Simulation: return fake OTP for testing
            return {
                'success': True,
                'message': 'OTP sent (simulation mode)',
                'otp': '123456',  # Test OTP
                'simulation': True
            }
        
        # In real Firebase, OTP is sent client-side
        return {
            'success': True,
            'message': 'Send OTP via Firebase client SDK',
            'simulation': False
        }
    
    def verify_id_token(self, id_token):
        """
        Verify Firebase ID token from client
        """
        if self.simulation_mode:
            # Simulation mode: accept test token
            if id_token == 'test_token_123456':
                return {
                    'success': True,
                    'uid': 'test_user_123',
                    'phone_number': '+911234567890',
                    'simulation': True
                }
            return {
                'success': False,
                'error': 'Invalid token',
                'simulation': True
            }
        
        try:
            decoded_token = auth.verify_id_token(id_token)
            return {
                'success': True,
                'uid': decoded_token['uid'],
                'phone_number': decoded_token.get('phone_number'),
                'email': decoded_token.get('email'),
                'simulation': False
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'simulation': False
            }
    
    def verify_otp(self, phone_number, otp):
        """
        Verify OTP (simulation mode only)
        In production, use verify_id_token instead
        """
        if self.simulation_mode:
            # Simulation: accept 123456 as valid OTP
            if otp == '123456':
                return {
                    'success': True,
                    'uid': f'sim_user_{phone_number[-4:]}',
                    'phone_number': phone_number,
                    'simulation': True
                }
            return {
                'success': False,
                'error': 'Invalid OTP',
                'simulation': True
            }
        
        return {
            'success': False,
            'error': 'Use verify_id_token for production',
            'simulation': False
        }
    
    def create_or_update_user(self, uid, phone_number=None, display_name=None, photo_url=None):
        """
        Create or update Firebase user
        """
        if self.simulation_mode:
            return {
                'success': True,
                'uid': uid,
                'simulation': True
            }
        
        try:
            update_data = {}
            if phone_number:
                update_data['phone_number'] = phone_number
            if display_name:
                update_data['display_name'] = display_name
            if photo_url:
                update_data['photo_url'] = photo_url
            
            user = auth.update_user(uid, **update_data)
            return {
                'success': True,
                'uid': user.uid,
                'simulation': False
            }
        except auth.UserNotFoundError:
            # Create new user
            try:
                user = auth.create_user(
                    uid=uid,
                    phone_number=phone_number,
                    display_name=display_name,
                    photo_url=photo_url
                )
                return {
                    'success': True,
                    'uid': user.uid,
                    'created': True,
                    'simulation': False
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'simulation': False
                }

# Singleton instance
firebase_service = FirebaseAuthService()
