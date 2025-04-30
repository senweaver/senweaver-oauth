"""
Coding认证源
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


class AuthCodingSource(BaseAuthSource):
    """
    Coding认证源
    """
    
    def __init__(self, config: AuthConfig, source: Optional[AuthSource] = None):
        """
        初始化
        
        Args:
            config: 认证配置
            source: 认证源，默认为Coding
        """
        super().__init__(
            config=config,
            source=source or AuthDefaultSource.CODING
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
            
            if 'error' in response or 'access_token' not in response:
                return AuthTokenResponse.failure(
                    message=response.get('error_description', '获取访问令牌失败')
                )
                
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
                'Authorization': f"token {token.access_token}",
                'Accept': 'application/json'
            }
            
            response = self.http_client.get(self.source.user_info_url, headers=headers)
            
            if 'error' in response or 'code' in response and response.get('code') != 0:
                error_msg = response.get('error_description') or response.get('msg', '获取用户信息失败')
                return AuthUserResponse.failure(error_msg)
            
            # Coding API返回的用户数据
            user_data = response.get('data', {})
            if not user_data and 'id' in response:
                user_data = response  # 有时API直接返回用户信息
            
            # 构建用户信息
            user = AuthUser(
                uuid=str(user_data.get('id')),
                username=user_data.get('name', ''),
                nickname=user_data.get('name'),
                avatar=user_data.get('avatar'),
                blog=user_data.get('home_page'),
                company=user_data.get('company'),
                location=user_data.get('location'),
                email=user_data.get('email'),
                gender=AuthGender.UNKNOWN,
                source=self.source.name,
                token=token,
                raw_user_info=response
            )
            
            return AuthUserResponse.success(user)
            
        except Exception as e:
            return AuthUserResponse.error(f"获取用户信息异常: {str(e)}") 