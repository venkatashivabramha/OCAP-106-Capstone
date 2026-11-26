"""
JWT Authentication backend — uses simplejwt tokens with Django built-in User
"""
from rest_framework_simplejwt.authentication import JWTAuthentication as SimpleJWTAuth
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework import exceptions


class JWTAuthentication(SimpleJWTAuth):
    """
    Thin wrapper around simplejwt so the REST_FRAMEWORK setting
    'authentication.backends.JWTAuthentication' still resolves correctly.
    """
    pass
