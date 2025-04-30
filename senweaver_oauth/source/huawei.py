"""
华为认证源
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


class AuthHuaweiSource(BaseAuthSource):
    """
    华为认证源
    """
    
    def __init__(self, config: AuthConfig, source: Optional[AuthSource] = None):
        """
        初始化
        
        Args:
            config: 认证配置
            source: 认证源，默认为华为
        """
        super().__init__(
            config=config,
            source=source or AuthDefaultSource.HUAWEI
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
            'Content-Type': 'application/x-www-form-urlencoded',
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
            
            id_token = response.get('id_token')
            if id_token:
                token.ext_data = {'id_token': id_token}
            
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
            # 华为接口需要构建特定请求参数
            method = 'opDetail'
            service = 'hwaccount'
            
            params = {
                'method': method,
                'service': service,
                'nsp_ts': str(int(time.time())),
                'nsp_fmt': 'JSON',
                'access_token': token.access_token
            }
            
            response = self.http_client.get(self.source.user_info_url, params=params)
            
            # 检查返回结果
            if response.get('nsp_status') != 0:
                return AuthUserResponse.failure(response.get('nsp_message', '获取用户信息失败'))
            
            # 解析用户数据
            user_data = response.get('user', {})
            
            # 解析性别
            gender = AuthGender.UNKNOWN
            if user_data.get('gender') == '1':
                gender = AuthGender.MALE
            elif user_data.get('gender') == '2':
                gender = AuthGender.FEMALE
            
            user = AuthUser(
                uuid=user_data.get('userID'),
                username=user_data.get('userName', ''),
                nickname=user_data.get('displayName'),
                avatar=user_data.get('headPictureURL'),
                email=user_data.get('email'),
                mobile=user_data.get('mobileNumber'),
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
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        
        try:
            response = self.http_client.post(
                self.source.access_token_url,  # 华为使用相同的URL刷新令牌
                data=params,
                headers=headers
            )
            
            if 'error' in response:
                return AuthTokenResponse.failure(
                    message=response.get('error_description', '刷新访问令牌失败')
                )
                
            token = AuthToken(
                access_token=response.get('access_token'),
                token_type=response.get('token_type', 'Bearer'),
                refresh_token=response.get('refresh_token', refresh_token),
                expires_in=response.get('expires_in', 0),
                scope=response.get('scope')
            )
            
            id_token = response.get('id_token')
            if id_token:
                token.ext_data = {'id_token': id_token}
            
            return AuthTokenResponse.success(token)
            
        except Exception as e:
            return AuthTokenResponse.error(f"刷新访问令牌异常: {str(e)}") 