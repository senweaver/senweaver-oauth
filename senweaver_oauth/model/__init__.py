"""
模型定义
"""

from senweaver_oauth.model.auth_callback import AuthCallback
from senweaver_oauth.model.auth_token import AuthToken
from senweaver_oauth.model.auth_user import AuthUser
from senweaver_oauth.model.auth_response import AuthResponse, AuthTokenResponse, AuthUserResponse

__all__ = [
    'AuthCallback',
    'AuthToken', 
    'AuthUser',
    'AuthResponse',
    'AuthTokenResponse',
    'AuthUserResponse'
] 