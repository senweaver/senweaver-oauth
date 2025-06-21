"""
微博认证源
"""
import uuid
from typing import Dict, Optional

from senweaver_oauth.config import AuthConfig
from senweaver_oauth.enums.auth_scope import AuthScope
from senweaver_oauth.enums.auth_source import AuthDefaultSource, AuthSource
from senweaver_oauth.model.auth_callback import AuthCallback
from senweaver_oauth.model.auth_response import AuthTokenResponse, AuthUserResponse
from senweaver_oauth.model.auth_token import AuthToken
from senweaver_oauth.model.auth_user import AuthUser
from senweaver_oauth.source.base import BaseAuthSource
from senweaver_oauth.enums.auth_gender import AuthGender


class AuthWeiboSource(BaseAuthSource):
    """
    微博认证源
    实现新浪微博登录功能
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
            source=source or AuthDefaultSource.WEIBO
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
            token_type="Bearer",
            expires_in=data.get("expires_in", 0),
            refresh_token=data.get("refresh_token", ""),
            uid=data.get("uid", ""),
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
        
        Args:
            token: 访问令牌
            
        Returns:
            用户信息响应
        """
        # 微博API调用参数
        params = {
            "access_token": token.access_token,
            "uid": token.uid
        }
        
        response = self.http_client.get(self.source.user_info_url, params=params)
            
        data = response
        
        if "error" in data:
            return AuthUserResponse(
                code=data.get("error_code", 400),
                message=data.get("error", "获取用户信息失败")
            )
            
        # 如果获取用户信息成功，构建用户信息对象
        user = AuthUser(
            uuid=f"{self.source.name}_{data.get('id', '')}",
            username=data.get("screen_name", ""),
            nickname=data.get("name", ""),
            avatar=data.get("avatar_large", "") or data.get("profile_image_url", ""),
            gender=self._get_gender(data.get("gender", "")),
            email="",  # 微博API默认不返回邮箱
            location=data.get("location", ""),
            remark=data.get("description", ""),
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
        
        Args:
            token: 访问令牌
            
        Returns:
            刷新后的访问令牌响应
        """
        # 微博不支持刷新token
        return AuthTokenResponse(
            code=400,
            message="微博不支持刷新token"
        )
        
    def revoke_token(self, token: AuthToken) -> bool:
        """
        撤销访问令牌
        
        Args:
            token: 访问令牌
            
        Returns:
            是否成功
        """
        if not self.source.revoke_token_url:
            return False
            
        params = {
            "access_token": token.access_token
        }
        
        response = self.http_client.get(self.source.revoke_token_url, params=params)
        
        # 如果返回结果包含"result=true"，则表示撤销成功
        return "result=true" in response.text
        
    def _get_gender(self, gender: str) -> AuthGender:
        """
        转换性别编码
        
        微博API性别：m表示男性，f表示女性，n表示未知
        
        Args:
            gender: 性别代码
            
        Returns:
            性别枚举
        """
        if gender == "m":
            return AuthGender.MALE
        elif gender == "f":
            return AuthGender.FEMALE
        else:
            return AuthGender.UNKNOWN 