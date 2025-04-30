"""
今日头条认证源
实现今日头条登录功能
"""
from typing import Dict, Optional, Any

from senweaver_oauth.config import AuthConfig
from senweaver_oauth.enums.auth_source import AuthDefaultSource, AuthSource
from senweaver_oauth.enums.auth_gender import AuthGender
from senweaver_oauth.model.auth_callback import AuthCallback
from senweaver_oauth.model.auth_response import AuthTokenResponse, AuthUserResponse
from senweaver_oauth.model.auth_token import AuthToken
from senweaver_oauth.model.auth_user import AuthUser
from senweaver_oauth.source.base import BaseAuthSource


class AuthToutiaoSource(BaseAuthSource):
    """
    今日头条认证源
    实现今日头条登录功能
    """
    
    def __init__(self, config: AuthConfig, source: Optional[AuthSource] = None):
        """
        初始化
        
        Args:
            config: 认证配置
            source: 认证源
        """
        super().__init__(
            config=config,
            source=source or AuthDefaultSource.TOUTIAO
        )
    
    def get_authorize_params(self, state: Optional[str] = None) -> Dict[str, Any]:
        """
        获取授权参数
        
        Args:
            state: 自定义state参数，用于防止CSRF攻击
            
        Returns:
            授权参数
        """
        return {
            'response_type': 'code',
            'client_key': self.config.client_id,
            'redirect_uri': self.config.redirect_uri,
            'auth_only': 1,  # 只进行授权，不进行登录
            'display': 0,    # 页面展示方式，0表示PC页面显示
            'state': state or self.get_state()
        }
    
    def build_authorize_url(self, params: Dict[str, Any]) -> str:
        """
        构建授权URL
        
        Args:
            params: 授权参数
            
        Returns:
            授权URL
        """
        return self.build_url(self.source.authorize_url, params)
    
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
            'client_key': self.config.client_id,
            'client_secret': self.config.client_secret,
            'grant_type': 'authorization_code'
        }
        
        try:
            response = self.http_client.post(self.source.access_token_url, params)
            
            if response.get('error_code', 0) != 0:
                return AuthTokenResponse.failure(
                    message=response.get('description', '获取访问令牌失败')
                )
                
            token = AuthToken(
                access_token=response.get('access_token'),
                token_type=response.get('token_type', 'Bearer'),
                expires_in=response.get('expires_in', 0),
                refresh_token=response.get('refresh_token'),
                open_id=response.get('open_id'),
                scope=None,
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
        if not token or not token.access_token:
            return AuthUserResponse.failure("访问令牌不能为空")
            
        params = {
            'access_token': token.access_token,
            'client_key': self.config.client_id
        }
        
        try:
            response = self.http_client.get(self.source.user_info_url, params)
            
            if response.get('error_code', 0) != 0:
                return AuthUserResponse.failure(
                    message=response.get('description', '获取用户信息失败')
                )
                
            # 获取用户信息
            user_data = response.get('data', {})
            
            # 判断是否是匿名用户
            is_anonymous = user_data.get('uid_type', 0) == 14
            anonymous_name = "匿名用户"
            
            user = AuthUser(
                uuid=user_data.get('uid'),
                username=anonymous_name if is_anonymous else user_data.get('screen_name'),
                nickname=anonymous_name if is_anonymous else user_data.get('screen_name'),
                avatar=user_data.get('avatar_url'),
                remark=user_data.get('description'),
                gender=AuthGender.get_gender(user_data.get('gender')),
                token=token,
                source=self.source.name,
                raw_user_info=user_data
            )
            
            return AuthUserResponse.success(user)
            
        except Exception as e:
            return AuthUserResponse.error(f"获取用户信息异常: {str(e)}") 