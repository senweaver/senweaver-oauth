"""
酷家乐认证源
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


class AuthKujialeSource(BaseAuthSource):
    """
    酷家乐认证源
    """
    
    def __init__(self, config: AuthConfig, source: Optional[AuthSource] = None):
        """
        初始化
        
        Args:
            config: 认证配置
            source: 认证源，默认为酷家乐
        """
        super().__init__(
            config=config,
            source=source or AuthDefaultSource.KUJIALE
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
            
            if response.get('code') != 0:
                return AuthTokenResponse.failure(
                    message=response.get('msg', '获取访问令牌失败')
                )
                
            # 解析数据
            data = response.get('data', {})
            
            token = AuthToken(
                access_token=data.get('access_token'),
                token_type=data.get('token_type', 'Bearer'),
                refresh_token=data.get('refresh_token'),
                expires_in=data.get('expires_in', 0),
                scope=data.get('scope'),
                code=callback.code
            )
            
            # 保存额外信息
            token.ext_data = {
                'uid': data.get('uid', ''),
                'open_id': data.get('openid', '')
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
            headers = {
                'Authorization': f"Bearer {token.access_token}",
                'Accept': 'application/json'
            }
            
            response = self.http_client.get(self.source.user_info_url, headers=headers)
            
            if response.get('code') != 0:
                return AuthUserResponse.failure(response.get('msg', '获取用户信息失败'))
            
            # 解析用户数据
            user_data = response.get('data', {})
            
            # 提取UID
            uid = ''
            if hasattr(token, 'ext_data') and token.ext_data:
                uid = token.ext_data.get('uid', '')
                
            if not uid and 'uid' in user_data:
                uid = user_data.get('uid')
                
            user = AuthUser(
                uuid=uid,
                username=user_data.get('username', ''),
                nickname=user_data.get('name'),
                avatar=user_data.get('avatar'),
                email=user_data.get('email'),
                mobile=user_data.get('phone'),
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
            
            if response.get('code') != 0:
                return AuthTokenResponse.failure(
                    message=response.get('msg', '刷新访问令牌失败')
                )
                
            # 解析数据
            data = response.get('data', {})
            
            token = AuthToken(
                access_token=data.get('access_token'),
                token_type=data.get('token_type', 'Bearer'),
                refresh_token=data.get('refresh_token', refresh_token),
                expires_in=data.get('expires_in', 0),
                scope=data.get('scope')
            )
            
            # 保存额外信息
            token.ext_data = {
                'uid': data.get('uid', ''),
                'open_id': data.get('openid', '')
            }
            
            return AuthTokenResponse.success(token)
            
        except Exception as e:
            return AuthTokenResponse.error(f"刷新访问令牌异常: {str(e)}") 