"""
抖音认证源
"""
import uuid
from typing import Dict, Optional

from senweaver_oauth.config import AuthConfig
from senweaver_oauth.enums.auth_scope import AuthScope
from senweaver_oauth.enums.auth_source import AuthDefaultSource, AuthSource
from senweaver_oauth.enums.auth_gender import AuthGender
from senweaver_oauth.model.auth_callback import AuthCallback
from senweaver_oauth.model.auth_response import AuthTokenResponse, AuthUserResponse
from senweaver_oauth.model.auth_token import AuthToken
from senweaver_oauth.model.auth_user import AuthUser
from senweaver_oauth.source.base import BaseAuthSource


class AuthDouyinSource(BaseAuthSource):
    """
    抖音认证源
    实现抖音登录功能
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
            source=source or AuthDefaultSource.DOUYIN
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
            "client_key": self.config.client_id,
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
        
        抖音API需要使用client_key和client_secret
        
        Args:
            callback: 授权回调参数
            
        Returns:
            访问令牌响应
        """
        params = {
            "client_key": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": callback.code,
            "grant_type": "authorization_code"
        }
        
        response = self.http_client.get(self.source.access_token_url, params=params)
        
            
        data = response
        
        # 抖音API返回格式：{"data": {...}, "message": "success"}
        if data.get("message") != "success":
            return AuthTokenResponse(
                code=400,
                message=f"获取访问令牌失败: {data.get('message', '')}"
            )
            
        token_data = data.get("data", {})
        
        token = AuthToken(
            access_token=token_data.get("access_token", ""),
            token_type="Bearer",
            expires_in=token_data.get("expires_in", 0),
            refresh_token=token_data.get("refresh_token", ""),
            open_id=token_data.get("open_id", ""),
            scope=token_data.get("scope", "")
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
        params = {
            "access_token": token.access_token,
            "open_id": token.open_id
        }
        
        response = self.http_client.get(self.source.user_info_url, params=params)
                    
        data = response
        
        # 抖音API返回格式：{"data": {...}, "message": "success"}
        if data.get("message") != "success":
            return AuthUserResponse(
                code=400,
                message=f"获取用户信息失败: {data.get('message', '')}"
            )
            
        user_data = data.get("data", {})
        
        # 构建用户信息
        user = AuthUser(
            uuid=f"{self.source.name}_{token.open_id}",
            username=user_data.get("nickname", ""),
            nickname=user_data.get("nickname", ""),
            avatar=user_data.get("avatar", ""),
            gender=self._get_gender(user_data.get("gender", 0)),
            email="",
            token=token,
            source=self.source.name,
            raw_user_info=user_data
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
            "client_key": self.config.client_id,
            "client_secret": self.config.client_secret,
            "refresh_token": token.refresh_token,
            "grant_type": "refresh_token"
        }
        
        response = self.http_client.get(self.source.refresh_token_url, params=params)
                    
        data = response
        
        # 抖音API返回格式：{"data": {...}, "message": "success"}
        if data.get("message") != "success":
            return AuthTokenResponse(
                code=400,
                message=f"刷新访问令牌失败: {data.get('message', '')}"
            )
            
        token_data = data.get("data", {})
        
        new_token = AuthToken(
            access_token=token_data.get("access_token", ""),
            token_type="Bearer",
            expires_in=token_data.get("expires_in", 0),
            refresh_token=token_data.get("refresh_token", token.refresh_token),
            open_id=token.open_id,
            scope=token_data.get("scope", token.scope)
        )
        
        return AuthTokenResponse(
            code=200,
            message="刷新访问令牌成功",
            data=new_token
        )
        
    def revoke_token(self, token: AuthToken) -> bool:
        """
        撤销访问令牌
        
        Args:
            token: 访问令牌
            
        Returns:
            是否成功
        """
        # 抖音不支持撤销令牌接口
        return False
        
    def _get_gender(self, gender: int) -> AuthGender:
        """
        转换性别编码
        
        抖音API性别：0表示未知，1表示男性，2表示女性
        
        Args:
            gender: 性别代码
            
        Returns:
            性别枚举
        """
        if gender == 1:
            return AuthGender.MALE
        elif gender == 2:
            return AuthGender.FEMALE
        else:
            return AuthGender.UNKNOWN 