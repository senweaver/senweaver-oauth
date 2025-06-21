"""
领英认证源
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


class AuthLinkedinSource(BaseAuthSource):
    """
    领英认证源
    实现LinkedIn登录功能
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
            source=source or AuthDefaultSource.LINKEDIN
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
            "redirect_uri": self.config.redirect_uri,
            "grant_type": "authorization_code"
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        response = self.http_client.post(
            self.source.access_token_url, 
            data=params,
            headers=headers
        )
                    
        data = response
        
        if "error" in data:
            return AuthTokenResponse(
                code=400,
                message=f"获取访问令牌失败: {data.get('error_description', data.get('error', ''))}"
            )
            
        token = AuthToken(
            access_token=data.get("access_token", ""),
            token_type=data.get("token_type", ""),
            expires_in=data.get("expires_in", 0),
            refresh_token=data.get("refresh_token", ""),
            scope=data.get("scope", "")
        )
        
        return AuthTokenResponse(
            code=200,
            message="获取访问令牌成功",
            data=token
        )
        
    def get_user_info(self, token: AuthToken, **kwargs) -> AuthUserResponse:
        """
        获取用户信息
        
        LinkedIn API v2需要分别获取用户基本信息和邮箱
        
        Args:
            token: 访问令牌
            
        Returns:
            用户信息响应
        """
        # 获取用户基本信息
        profile_url = self.source.user_info_url
        email_url = "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))"
        
        headers = {
            "Authorization": f"Bearer {token.access_token}"
        }
        
        # 获取基本资料
        profile_response = self.http_client.get(profile_url, headers=headers)
                    
        profile_data = profile_response
        
        # 获取邮箱
        email_response = self.http_client.get(email_url, headers=headers)
        email = ""
        
        if email_response:
            email_data = email_response
            elements = email_data.get("elements", [])
            if elements and "handle~" in elements[0]:
                email = elements[0]["handle~"].get("emailAddress", "")
        
        # 构建用户信息
        user_id = profile_data.get("id", "")
        first_name = profile_data.get("localizedFirstName", "")
        last_name = profile_data.get("localizedLastName", "")
        full_name = f"{first_name} {last_name}".strip()
        
        # 获取头像（可能需要额外请求）
        avatar = ""
        
        user = AuthUser(
            uuid=f"{self.source.name}_{user_id}",
            username=full_name,
            nickname=full_name,
            avatar=avatar,
            gender=AuthGender.UNKNOWN,  # LinkedIn API不返回性别信息
            email=email,
            token=token,
            source=self.source.name,
            raw_user_info={"profile": profile_data, "email": email}
        )
        
        return AuthUserResponse(
            code=200,
            message="获取用户信息成功",
            data=user
        )
        
    def refresh_token(self, token: AuthToken) -> AuthTokenResponse:
        """
        刷新访问令牌
        
        Args:
            token: 访问令牌
            
        Returns:
            刷新后的访问令牌响应
        """
        if not self.source.refresh_token_url or not token.refresh_token:
            return AuthTokenResponse(
                code=400,
                message="不支持刷新访问令牌"
            )
            
        params = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "refresh_token": token.refresh_token,
            "grant_type": "refresh_token"
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        response = self.http_client.post(
            self.source.refresh_token_url, 
            data=params,
            headers=headers
        )
        
            
        data = response
        
        if "error" in data:
            return AuthTokenResponse(
                code=400,
                message=f"刷新访问令牌失败: {data.get('error_description', data.get('error', ''))}"
            )
            
        token = AuthToken(
            access_token=data.get("access_token", ""),
            token_type=data.get("token_type", ""),
            expires_in=data.get("expires_in", 0),
            refresh_token=data.get("refresh_token", token.refresh_token),
            scope=data.get("scope", "")
        )
        
        return AuthTokenResponse(
            code=200,
            message="刷新访问令牌成功",
            data=token
        )
        
    def revoke_token(self, token: AuthToken) -> bool:
        """
        撤销访问令牌
        
        Args:
            token: 访问令牌
            
        Returns:
            是否成功
        """
        # LinkedIn目前不支持通过API撤销令牌
        return False 