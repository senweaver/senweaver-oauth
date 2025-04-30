"""
Stack Overflow认证源
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


class AuthStackOverflowSource(BaseAuthSource):
    """
    Stack Overflow认证源
    """
    
    def __init__(self, config: AuthConfig, source: Optional[AuthSource] = None):
        """
        初始化
        
        Args:
            config: 认证配置
            source: 认证源，默认为Stack Overflow
        """
        super().__init__(
            config=config,
            source=source or AuthDefaultSource.STACK_OVERFLOW
        )
        
    def get_authorize_params(self) -> dict:
        """
        获取授权参数
        
        Returns:
            授权参数
        """
        params = super().get_authorize_params()
        # Stack Overflow API需要指定范围
        # 常用scope：read_inbox,no_expiry,write_access,private_info
        if not params.get('scope'):
            params['scope'] = 'private_info'
        if not params.get('key'):
            params['key'] = self.config.client_id  # Stack Overflow API还需要一个key参数
        return params
        
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
        
        try:
            response = self.http_client.post(
                self.source.access_token_url, 
                data=params
            )
            
            if 'access_token' not in response:
                error_msg = response.get('error_description') or response.get('error') or '获取访问令牌失败'
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
                'Authorization': f"Bearer {token.access_token}"
            }
            
            # Stack Overflow API需要添加site和key参数
            user_info_url = f"{self.source.user_info_url}?site=stackoverflow&key={self.config.client_id}"
            
            response = self.http_client.get(
                user_info_url,
                headers=headers
            )
            
            if 'items' not in response or not response['items']:
                error_msg = response.get('error_message') or response.get('error_name') or '获取用户信息失败'
                return AuthUserResponse.failure(error_msg)
            
            # Stack Overflow API返回的是items数组，取第一个元素
            user_info = response['items'][0]
            
            user = AuthUser(
                uuid=str(user_info.get('user_id')),
                username=user_info.get('display_name', ''),
                nickname=user_info.get('display_name', ''),
                avatar=user_info.get('profile_image'),
                email='',  # Stack Overflow API不直接返回邮箱
                location=user_info.get('location'),
                gender=AuthGender.UNKNOWN,
                source=self.source.name,
                token=token,
                raw_user_info=user_info
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
        # Stack Overflow API通常颁发的令牌不会过期(no_expiry scope)，因此大多数情况下不需要刷新
        if not self.source.refresh_token_url:
            return AuthTokenResponse.not_implemented("该平台不支持刷新令牌")
            
        params = {
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        try:
            response = self.http_client.post(
                self.source.refresh_token_url,
                data=params
            )
            
            if 'access_token' not in response:
                error_msg = response.get('error_description') or response.get('error') or '刷新访问令牌失败'
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