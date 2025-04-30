"""
Slack认证源
"""

from typing import Optional, Dict

from senweaver_oauth.config import AuthConfig
from senweaver_oauth.enums.auth_gender import AuthGender
from senweaver_oauth.enums.auth_source import AuthDefaultSource, AuthSource
from senweaver_oauth.model.auth_callback import AuthCallback
from senweaver_oauth.model.auth_response import AuthTokenResponse, AuthUserResponse
from senweaver_oauth.model.auth_token import AuthToken
from senweaver_oauth.model.auth_user import AuthUser
from senweaver_oauth.source.base import BaseAuthSource


class AuthSlackSource(BaseAuthSource):
    """
    Slack认证源
    """
    
    def __init__(self, config: AuthConfig, source: Optional[AuthSource] = None):
        """
        初始化
        
        Args:
            config: 认证配置
            source: 认证源，默认为Slack
        """
        super().__init__(
            config=config,
            source=source or AuthDefaultSource.SLACK
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
            'redirect_uri': self.config.redirect_uri
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
            
            if not response.get('ok', False):
                return AuthTokenResponse.failure(
                    message=response.get('error', '获取访问令牌失败')
                )
                
            # Slack返回的数据结构比较特殊
            token = AuthToken(
                access_token=response.get('access_token'),
                token_type=response.get('token_type', 'Bearer'),
                refresh_token=None,  # Slack不支持刷新Token
                expires_in=0,  # Slack Token没有过期时间
                scope=response.get('scope'),
                code=callback.code
            )
            
            # 保存额外信息，用于获取用户信息
            token.ext_data = {
                'team_id': response.get('team', {}).get('id'),
                'user_id': response.get('authed_user', {}).get('id')
            }
            
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
            # 从token中获取用户ID
            user_id = None
            if hasattr(token, 'ext_data') and isinstance(token.ext_data, Dict):
                user_id = token.ext_data.get('user_id')
                
            if not user_id:
                return AuthUserResponse.failure("无法获取用户ID")
            
            # 构建请求参数
            params = {
                'user': user_id
            }
            
            headers = {
                'Authorization': f"Bearer {token.access_token}",
                'Accept': 'application/json'
            }
            
            response = self.http_client.get(
                self.source.user_info_url, 
                params=params,
                headers=headers
            )
            
            if not response.get('ok', False):
                return AuthUserResponse.failure(response.get('error', '获取用户信息失败'))
            
            # 获取用户信息
            user_info = response.get('user', {})
            profile = user_info.get('profile', {})
            
            # 构建用户信息
            user = AuthUser(
                uuid=user_info.get('id'),
                username=user_info.get('name', ''),
                nickname=profile.get('display_name') or profile.get('real_name'),
                avatar=profile.get('image_192') or profile.get('image_72'),
                email=profile.get('email'),
                gender=AuthGender.UNKNOWN,
                source=self.source.name,
                token=token,
                raw_user_info=response
            )
            
            return AuthUserResponse.success(user)
            
        except Exception as e:
            return AuthUserResponse.error(f"获取用户信息异常: {str(e)}") 