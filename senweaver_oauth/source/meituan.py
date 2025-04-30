"""
美团认证源
"""

from typing import Optional
import time
import hashlib

from senweaver_oauth.config import AuthConfig
from senweaver_oauth.enums.auth_gender import AuthGender
from senweaver_oauth.enums.auth_source import AuthDefaultSource, AuthSource
from senweaver_oauth.model.auth_callback import AuthCallback
from senweaver_oauth.model.auth_response import AuthTokenResponse, AuthUserResponse
from senweaver_oauth.model.auth_token import AuthToken
from senweaver_oauth.model.auth_user import AuthUser
from senweaver_oauth.source.base import BaseAuthSource


class AuthMeituanSource(BaseAuthSource):
    """
    美团认证源
    """
    
    def __init__(self, config: AuthConfig, source: Optional[AuthSource] = None):
        """
        初始化
        
        Args:
            config: 认证配置
            source: 认证源，默认为美团
        """
        super().__init__(
            config=config,
            source=source or AuthDefaultSource.MEITUAN
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
                
            # 提取数据
            token = AuthToken(
                access_token=response.get('access_token'),
                token_type=response.get('token_type', 'Bearer'),
                refresh_token=response.get('refresh_token'),
                expires_in=response.get('expires_in', 0),
                scope=response.get('scope'),
                code=callback.code
            )
            
            # 保存app_id，用于计算签名
            token.ext_data = {
                'app_id': self.config.client_id
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
            # 美团接口需要签名
            timestamp = str(int(time.time()))
            app_id = self.config.client_id
            
            # 计算签名（简化版）
            sign_str = f"{app_id}{timestamp}{self.config.client_secret}"
            sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
            
            params = {
                'app_id': app_id,
                'access_token': token.access_token,
                'timestamp': timestamp,
                'sign': sign
            }
            
            response = self.http_client.get(
                self.source.user_info_url, 
                params=params
            )
            
            if response.get('status') != 'success':
                return AuthUserResponse.failure(response.get('error', {}).get('message', '获取用户信息失败'))
            
            # 获取用户数据
            user_data = response.get('data', {})
            
            user = AuthUser(
                uuid=user_data.get('openid'),
                username=user_data.get('username', ''),
                nickname=user_data.get('nickname'),
                avatar=user_data.get('avatar'),
                gender=AuthGender.UNKNOWN,
                source=self.source.name,
                token=token,
                raw_user_info=response
            )
            
            return AuthUserResponse.success(user)
            
        except Exception as e:
            return AuthUserResponse.error(f"获取用户信息异常: {str(e)}") 