"""
人人网认证源
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


class AuthRenrenSource(BaseAuthSource):
    """
    人人网认证源
    """
    
    def __init__(self, config: AuthConfig, source: Optional[AuthSource] = None):
        """
        初始化
        
        Args:
            config: 认证配置
            source: 认证源，默认为人人网
        """
        super().__init__(
            config=config,
            source=source or AuthDefaultSource.RENREN
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
            params = {
                'access_token': token.access_token,
                'format': 'json'
            }
            
            response = self.http_client.get(
                self.source.user_info_url, 
                params=params
            )
            
            if 'error' in response:
                return AuthUserResponse.failure(response.get('error_description', '获取用户信息失败'))
            
            # 人人网API返回的响应结构
            response_data = response
            if 'response' in response:
                response_data = response.get('response')
            
            # 返回的用户信息
            gender = AuthGender.UNKNOWN
            if response_data.get('sex') == 1:
                gender = AuthGender.MALE
            elif response_data.get('sex') == 0:
                gender = AuthGender.FEMALE
            
            user = AuthUser(
                uuid=str(response_data.get('id')),
                username=response_data.get('name', ''),
                nickname=response_data.get('screen_name'),
                avatar=response_data.get('avatar', {}).get('large'),
                email=response_data.get('email'),
                gender=gender,
                source=self.source.name,
                token=token,
                raw_user_info=response
            )
            
            return AuthUserResponse.success(user)
            
        except Exception as e:
            return AuthUserResponse.error(f"获取用户信息异常: {str(e)}") 