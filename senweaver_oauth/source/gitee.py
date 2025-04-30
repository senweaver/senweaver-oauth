"""
Gitee认证源
"""

from senweaver_oauth.enums.auth_gender import AuthGender
from senweaver_oauth.config import AuthConfig
from senweaver_oauth.enums.auth_source import AuthDefaultSource
from senweaver_oauth.model.auth_callback import AuthCallback
from senweaver_oauth.model.auth_response import AuthTokenResponse, AuthUserResponse
from senweaver_oauth.model.auth_token import AuthToken
from senweaver_oauth.model.auth_user import AuthUser
from senweaver_oauth.source.base import BaseAuthSource
from typing import Optional
from senweaver_oauth.enums.auth_source import AuthSource

class AuthGiteeSource(BaseAuthSource):
    """
    Gitee认证源
    """
    
    def __init__(self, config: AuthConfig, source: Optional[AuthSource] = None):
        """
        初始化
        
        Args:
            config: 认证配置
        """
        super().__init__(
            config=config,
            source=source or AuthDefaultSource.GITEE
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
            'grant_type': 'authorization_code',
            'code': callback.code,
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret,
            'redirect_uri': self.config.redirect_uri
        }
        
        try:
            response = self.http_client.post(self.source.access_token_url, data=params)
            
            if 'error' in response:
                return AuthTokenResponse.failure(
                    message=response.get('error_description', '获取访问令牌失败')
                )
                
            token = AuthToken(
                access_token=response.get('access_token'),
                token_type=response.get('token_type'),
                expires_in=response.get('expires_in', 7200),
                refresh_token=response.get('refresh_token'),
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
            headers = {'Authorization': f"Bearer {token.access_token}"}
            response = self.http_client.get(self.source.user_info_url, headers=headers)
            
            if 'message' in response and response.get('message') != 'success':
                return AuthUserResponse.failure(response.get('message', '获取用户信息失败'))
                
            user = AuthUser(
                uuid=str(response.get('id')),
                username=response.get('login'),
                nickname=response.get('name'),
                avatar=response.get('avatar_url'),
                blog=response.get('blog'),
                company=response.get('company'),
                location=response.get('location'),
                email=response.get('email'),
                remark=response.get('bio'),
                gender=AuthGender.UNKNOWN,  # Gitee API不返回性别
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
        params = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret
        }
        
        try:
            response = self.http_client.post(self.source.refresh_token_url, data=params)
            
            if 'error' in response:
                return AuthTokenResponse.failure(
                    message=response.get('error_description', '刷新访问令牌失败')
                )
                
            token = AuthToken(
                access_token=response.get('access_token'),
                token_type=response.get('token_type'),
                expires_in=response.get('expires_in', 7200),
                refresh_token=response.get('refresh_token'),
                scope=response.get('scope')
            )
            
            return AuthTokenResponse.success(token)
            
        except Exception as e:
            return AuthTokenResponse.error(f"刷新访问令牌异常: {str(e)}") 