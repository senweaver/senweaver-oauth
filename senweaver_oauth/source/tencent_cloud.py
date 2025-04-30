"""
腾讯云认证源
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


class AuthTencentCloudSource(BaseAuthSource):
    """
    腾讯云认证源
    """
    
    def __init__(self, config: AuthConfig, source: Optional[AuthSource] = None):
        """
        初始化
        
        Args:
            config: 认证配置
            source: 认证源，默认为腾讯云
        """
        super().__init__(
            config=config,
            source=source or AuthDefaultSource.TENCENT_CLOUD
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
            
            # 检查返回结果
            if 'data' not in response or 'access_token' not in response.get('data', {}):
                if 'code' in response and 'message' in response:
                    return AuthTokenResponse.failure(message=response.get('message', '获取访问令牌失败'))
                return AuthTokenResponse.failure(message='获取访问令牌失败')
            
            # 获取数据
            data = response.get('data', {})
            
            token = AuthToken(
                access_token=data.get('access_token'),
                token_type=data.get('token_type', 'Bearer'),
                refresh_token=data.get('refresh_token'),
                expires_in=data.get('expires_in', 0),
                scope=data.get('scope'),
                code=callback.code
            )
            
            # 保存用户ID，用于获取用户信息
            if 'open_id' in data:
                token.ext_data = {'open_id': data.get('open_id')}
            
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
            
            # 获取用户信息
            response = self.http_client.get(
                self.source.user_info_url,
                headers=headers
            )
            
            # 检查返回结果
            if 'data' not in response:
                if 'code' in response and 'message' in response:
                    return AuthUserResponse.failure(response.get('message', '获取用户信息失败'))
                return AuthUserResponse.failure('获取用户信息失败')
            
            # 获取用户数据
            user_data = response.get('data', {})
            
            # 提取OpenID
            open_id = ''
            if hasattr(token, 'ext_data') and token.ext_data:
                open_id = token.ext_data.get('open_id', '')
            
            # 构建用户信息
            user = AuthUser(
                uuid=open_id or user_data.get('id'),
                username=user_data.get('name', ''),
                nickname=user_data.get('nick'),
                avatar=user_data.get('avatar'),
                email=user_data.get('email'),
                gender=AuthGender.UNKNOWN,
                source=self.source.name,
                token=token,
                raw_user_info=response
            )
            
            return AuthUserResponse.success(user)
            
        except Exception as e:
            return AuthUserResponse.error(f"获取用户信息异常: {str(e)}") 