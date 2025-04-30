"""
饿了么认证源
"""

from typing import Optional
import time

from senweaver_oauth.config import AuthConfig
from senweaver_oauth.enums.auth_gender import AuthGender
from senweaver_oauth.enums.auth_source import AuthDefaultSource, AuthSource
from senweaver_oauth.model.auth_callback import AuthCallback
from senweaver_oauth.model.auth_response import AuthTokenResponse, AuthUserResponse
from senweaver_oauth.model.auth_token import AuthToken
from senweaver_oauth.model.auth_user import AuthUser
from senweaver_oauth.source.base import BaseAuthSource


class AuthElemeSource(BaseAuthSource):
    """
    饿了么认证源
    """
    
    def __init__(self, config: AuthConfig, source: Optional[AuthSource] = None):
        """
        初始化
        
        Args:
            config: 认证配置
            source: 认证源，默认为饿了么
        """
        super().__init__(
            config=config,
            source=source or AuthDefaultSource.ELEME
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
            'grant_type': 'authorization_code'
        }
        
        headers = {
            'Accept': 'application/json'
        }
        
        try:
            response = self.http_client.post(
                self.source.access_token_url, 
                data=params,
                headers=headers
            )
            
            if 'error' in response:
                return AuthTokenResponse.failure(
                    message=response.get('error_description', '获取访问令牌失败')
                )
                
            # 计算过期时间
            expires_in = response.get('expires_in', 0)
            if expires_in:
                expires_in = int(expires_in)
                
            token = AuthToken(
                access_token=response.get('access_token'),
                token_type=response.get('token_type', 'Bearer'),
                refresh_token=response.get('refresh_token'),
                expires_in=expires_in,
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
            response = self.http_client.get(self.source.user_info_url, headers=headers)
            
            if 'error' in response or response.get('status') != 'success':
                error_msg = response.get('error_description') or response.get('message') or '获取用户信息失败'
                return AuthUserResponse.failure(error_msg)
            
            # 获取用户信息
            user_info = response.get('data', {})
            
            user = AuthUser(
                uuid=str(user_info.get('userId')),
                username=user_info.get('userName', ''),
                nickname=user_info.get('shopName'),
                avatar=user_info.get('shopLogo'),
                mobile=user_info.get('mobile'),
                email=user_info.get('email'),
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
            'refresh_token': refresh_token,
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret,
            'grant_type': 'refresh_token'
        }
        
        headers = {
            'Accept': 'application/json'
        }
        
        try:
            response = self.http_client.post(
                self.source.refresh_token_url,
                data=params,
                headers=headers
            )
            
            if 'error' in response:
                return AuthTokenResponse.failure(
                    message=response.get('error_description', '刷新访问令牌失败')
                )
            
            # 计算过期时间
            expires_in = response.get('expires_in', 0)
            if expires_in:
                expires_in = int(expires_in)
                
            token = AuthToken(
                access_token=response.get('access_token'),
                token_type=response.get('token_type', 'Bearer'),
                refresh_token=response.get('refresh_token', refresh_token),
                expires_in=expires_in,
                scope=response.get('scope')
            )
            
            return AuthTokenResponse.success(token)
            
        except Exception as e:
            return AuthTokenResponse.error(f"刷新访问令牌异常: {str(e)}") 