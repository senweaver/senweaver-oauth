"""
Facebook认证源
"""
import uuid
from typing import Dict, Optional

from senweaver_oauth.config import AuthConfig
from senweaver_oauth.enums.auth_scope import AuthScope
from senweaver_oauth.enums.auth_gender import AuthGender
from senweaver_oauth.enums.auth_source import AuthDefaultSource, AuthSource
from senweaver_oauth.model.auth_callback import AuthCallback
from senweaver_oauth.model.auth_response import AuthTokenResponse, AuthUserResponse
from senweaver_oauth.model.auth_token import AuthToken
from senweaver_oauth.model.auth_user import AuthUser
from senweaver_oauth.source.base import BaseAuthSource


class AuthFacebookSource(BaseAuthSource):
    """
    Facebook认证源
    实现Facebook登录
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
            source=source or AuthDefaultSource.FACEBOOK
        )
        
    def get_authorize_params(self, state: Optional[str] = None) -> Dict[str, str]:
        """
        获取授权参数
        
        Args:
            state: 自定义state参数，用于防止CSRF攻击
            
        Returns:
            授权参数
        """
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "response_type": "code",
            "scope": self.get_scopes(),
            "state": state or str(uuid.uuid4())
        }
        return params
        
    def build_authorize_url(self, params: Dict[str, str]) -> str:
        """
        构建授权URL
        
        Args:
            params: 授权参数
            
        Returns:
            授权URL
        """
        url = self.source.authorize_url
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{url}?{query}"
        
    def get_access_token(self, callback: AuthCallback) -> AuthTokenResponse:
        """
        获取访问令牌
        
        Args:
            callback: 授权回调参数
            
        Returns:
            访问令牌响应
        """
        params = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": callback.code,
            "redirect_uri": self.config.redirect_uri
        }
        
        response = self.http_client.get(self.source.access_token_url, params=params)
        
        data = response        
        if "error" in data:
            return AuthTokenResponse(
                code=400,
                message=f"获取访问令牌失败: {data.get('error', {}).get('message', '')}"
            )
            
        token = AuthToken(
            access_token=data.get("access_token", ""),
            token_type="Bearer",
            expires_in=data.get("expires_in", 0)
        )
        
        return AuthTokenResponse(
            code=200,
            message="获取访问令牌成功",
            data=token
        )
        
    def get_user_info(self, token: AuthToken, **kwargs) -> AuthUserResponse:
        """
        获取用户信息
        
        Args:
            token: 访问令牌
            
        Returns:
            用户信息响应
        """
        # Facebook Graph API的用户信息请求参数
        fields = "id,name,email,picture.type(large)"
        params = {
            "access_token": token.access_token,
            "fields": fields
        }
        
        response = self.http_client.get(self.source.user_info_url, params=params)
                    
        data = response
        
        if "error" in data:
            return AuthUserResponse(
                code=400,
                message=f"获取用户信息失败: {data.get('error', {}).get('message', '')}"
            )
            
        # 获取用户头像
        avatar = ""
        picture_data = data.get("picture", {}).get("data", {})
        if picture_data:
            avatar = picture_data.get("url", "")
            
        user = AuthUser(
            uuid=f"{self.source.name}_{data.get('id', '')}",
            username=data.get("name", ""),
            nickname=data.get("name", ""),
            avatar=avatar,
            gender=AuthGender.UNKNOWN,  # Facebook Graph API需要额外权限才能获取性别
            email=data.get("email", ""),
            token=token,
            source=self.source.name,
            raw_user_info=data
        )
        
        return AuthUserResponse(
            code=200,
            message="获取用户信息成功",
            data=user
        )
        
    def refresh_token(self, token: AuthToken) -> AuthTokenResponse:
        """
        刷新访问令牌
        
        Facebook用户访问令牌无法直接刷新，需要使用长效令牌
        标准的短期令牌有效期约为2小时，长期令牌有效期约为60天
        要获取长期令牌，需要在获取短期令牌后立即请求交换为长期令牌
        
        Args:
            token: 访问令牌
            
        Returns:
            刷新后的访问令牌响应
        """
        # Facebook不支持标准的刷新令牌操作
        return AuthTokenResponse(
            code=400,
            message="Facebook不支持刷新令牌"
        )
        
    def revoke_token(self, token: AuthToken) -> bool:
        """
        撤销访问令牌
        
        Args:
            token: 访问令牌
            
        Returns:
            是否成功
        """
        # Facebook支持撤销令牌
        revoke_url = "https://graph.facebook.com/me/permissions"
        params = {
            "access_token": token.access_token
        }
        
        response = self.http_client.delete(revoke_url, params=params)
        
        # 如果返回的success字段为true，则表示撤销成功
        data = response
        return data.get("success", False) 