"""
喜马拉雅认证源
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


class AuthXmlySource(BaseAuthSource):
    """
    喜马拉雅认证源
    """
    
    def __init__(self, config: AuthConfig, source: Optional[AuthSource] = None):
        """
        初始化
        
        Args:
            config: 认证配置
            source: 认证源，默认为喜马拉雅
        """
        super().__init__(
            config=config,
            source=source or AuthDefaultSource.XMLY
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
            
            if response.get('ret') != 0:
                return AuthTokenResponse.failure(
                    message=response.get('msg', '获取访问令牌失败')
                )
                
            # 提取令牌信息
            token_info = response.get('access_token', {})
            
            token = AuthToken(
                access_token=token_info.get('token'),
                token_type='Bearer',
                refresh_token=token_info.get('refresh_token'),
                expires_in=token_info.get('expires_in', 0),
                scope=params.get('scope'),
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
            
            params = {
                'app_key': self.config.client_id,
                'client_os_type': 3,  # 3表示Web
                'device_id': 'web'
            }
            
            response = self.http_client.get(
                self.source.user_info_url, 
                params=params,
                headers=headers
            )
            
            if response.get('ret') != 0:
                return AuthUserResponse.failure(response.get('msg', '获取用户信息失败'))
            
            # 获取用户信息
            user_data = response.get('data', {})
            
            # 处理性别信息
            gender = AuthGender.UNKNOWN
            if user_data.get('gender') == 1:
                gender = AuthGender.MALE
            elif user_data.get('gender') == 2:
                gender = AuthGender.FEMALE
                
            user = AuthUser(
                uuid=str(user_data.get('id')),
                username=user_data.get('nickname', ''),
                nickname=user_data.get('nickname'),
                avatar=user_data.get('avatar_url'),
                gender=gender,
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
            'device_id': 'web',
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
            
            if response.get('ret') != 0:
                return AuthTokenResponse.failure(
                    message=response.get('msg', '刷新访问令牌失败')
                )
            
            # 提取令牌信息
            token_info = response.get('access_token', {})
            
            token = AuthToken(
                access_token=token_info.get('token'),
                token_type='Bearer',
                refresh_token=token_info.get('refresh_token', refresh_token),
                expires_in=token_info.get('expires_in', 0),
                scope=None
            )
            
            return AuthTokenResponse.success(token)
            
        except Exception as e:
            return AuthTokenResponse.error(f"刷新访问令牌异常: {str(e)}") 