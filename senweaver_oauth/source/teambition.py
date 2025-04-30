"""
Teambition认证源
"""

from typing import Optional

from senweaver_oauth.config import AuthConfig
from senweaver_oauth.enums.auth_gender import AuthGender
from senweaver_oauth.enums.auth_source import AuthDefaultSource, AuthSource
from senweaver_oauth.model.auth_callback import AuthCallback
from senweaver_oauth.model.auth_response import AuthTokenResponse, AuthUserResponse
from senweaver_oauth.model.auth_token import AuthToken
from senweaver_oauth.model.auth_user import AuthUser
from senweaver_oauth.source.base import BaseAuthSource


class AuthTeambitionSource(BaseAuthSource):
    """
    Teambition认证源
    """
    
    def __init__(self, config: AuthConfig, source: Optional[AuthSource] = None):
        """
        初始化
        
        Args:
            config: 认证配置
            source: 认证源，默认为Teambition
        """
        super().__init__(
            config=config,
            source=source or AuthDefaultSource.TEAMBITION
        )
        
    def get_access_token(self, callback: AuthCallback) -> AuthTokenResponse:
        """
        获取访问令牌
        
        Args:
            callback: 回调参数
            
        Returns:
            访问令牌
        """
        if not callback.code:
            return AuthTokenResponse.failure("授权码不能为空")
            
        params = {
            'code': callback.code,
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret,
            'redirect_uri': self.config.redirect_uri,
            'grant_type': 'code'  # Teambition使用 'code' 而不是 'authorization_code'
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            response = self.http_client.post(
                self.source.access_token_url, 
                json=params,  # Teambition API使用JSON格式
                headers=headers
            )
            
            if 'access_token' not in response:
                error_msg = response.get('message') if 'message' in response else '获取访问令牌失败'
                return AuthTokenResponse.failure(message=error_msg)
                
            token = AuthToken(
                access_token=response.get('access_token'),
                token_type=response.get('token_type', 'Bearer'),
                refresh_token=response.get('refresh_token'),
                expires_in=response.get('expires_in', 0),
                scope=response.get('scope'),
                code=callback.code
            )
            
            return AuthTokenResponse.success(token)
            
        except Exception as e:
            return AuthTokenResponse.error(f"获取访问令牌异常: {str(e)}")
        
    def get_user_info(self, token: AuthToken, **kwargs) -> AuthUserResponse:
        """
        获取用户信息
        
        Args:
            token: 访问令牌
            
        Returns:
            用户信息
        """
        try:
            headers = {
                'Authorization': f"Bearer {token.access_token}",
                'Accept': 'application/json'
            }
            
            response = self.http_client.get(
                self.source.user_info_url,
                headers=headers
            )
            
            if 'message' in response and '_id' not in response:
                return AuthUserResponse.failure(response.get('message', '获取用户信息失败'))
            
            user = AuthUser(
                uuid=response.get('_id') or response.get('id'),  # Teambition使用_id作为用户ID
                username=response.get('name', ''),
                nickname=response.get('name'),
                avatar=response.get('avatarUrl'),
                email=response.get('email'),
                mobile=response.get('phone'),
                gender=AuthGender.UNKNOWN,
                source=self.source.name,
                token=token,
                raw_user_info=response
            )
            
            return AuthUserResponse.success(user)
            
        except Exception as e:
            return AuthUserResponse.error(f"获取用户信息异常: {str(e)}")
            
    def refresh_token(self, refresh_token: str) -> AuthTokenResponse:
        """
        刷新访问令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            新的访问令牌
        """
        if not self.source.refresh_token_url:
            return AuthTokenResponse.not_implemented("该平台不支持刷新令牌")
            
        params = {
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            response = self.http_client.post(
                self.source.refresh_token_url,
                json=params,  # Teambition API使用JSON格式
                headers=headers
            )
            
            if 'access_token' not in response:
                error_msg = response.get('message') if 'message' in response else '刷新访问令牌失败'
                return AuthTokenResponse.failure(message=error_msg)
                
            token = AuthToken(
                access_token=response.get('access_token'),
                token_type=response.get('token_type', 'Bearer'),
                refresh_token=response.get('refresh_token', refresh_token),
                expires_in=response.get('expires_in', 0),
                scope=response.get('scope')
            )
            
            return AuthTokenResponse.success(token)
            
        except Exception as e:
            return AuthTokenResponse.error(f"刷新访问令牌异常: {str(e)}") 