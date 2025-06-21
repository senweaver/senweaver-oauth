"""
百度认证源
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


class AuthBaiduSource(BaseAuthSource):
    """
    百度认证源
    实现百度账号登录功能
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
            source=source or AuthDefaultSource.BAIDU
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
            "state": state or str(uuid.uuid4()),
            "display": "popup"
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
        
        Args:
            token: 访问令牌
            
        Returns:
            用户信息响应
        """
        params = {
            "access_token": token.access_token,
            "format": "json"
        }
        
        response = self.http_client.get(
            self.source.user_info_url, 
            params=params
        )
        
            
        data = response
        
        if "error_code" in data:
            return AuthUserResponse(
                code=data.get("error_code", 400),
                message=data.get("error_msg", "获取用户信息失败")
            )
            
        # 解析百度用户信息
        user_id = data.get("userid", "") or data.get("openid", "")
        username = data.get("username", "") or data.get("uname", "")
        
        # 构建用户信息
        user = AuthUser(
            uuid=f"{self.source.name}_{user_id}",
            username=username,
            nickname=username,
            avatar=data.get("portrait", ""),  # 头像需要拼接成URL
            gender=self._get_gender(data.get("sex", "")),
            email="",  # 百度API默认不返回邮箱
            location="",
            token=token,
            source=self.source.name,
            raw_user_info=data
        )
        
        # 补全头像URL
        if user.avatar:
            user.avatar = f"http://tb.himg.baidu.com/sys/portrait/item/{user.avatar}"
        
        return AuthUserResponse(
            code=200,
            message="获取用户信息成功",
            data=user
        )
        
    def refresh_token(self, refresh_token: str) -> AuthTokenResponse:
        """
        刷新访问令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            刷新结果
        """
        if not self.source.refresh_token_url:
            return AuthTokenResponse(
                code=400,
                message="该平台不支持刷新令牌"
            )
            
        params = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "refresh_token": refresh_token,
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
            refresh_token=data.get("refresh_token", refresh_token),
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
        if not self.source.revoke_token_url:
            return False
            
        params = {
            "access_token": token.access_token
        }
        
        self.http_client.get(self.source.revoke_token_url, params=params)
        
        return True
        
    def _get_gender(self, gender: str) -> AuthGender:
        """
        转换性别编码
        
        Args:
            gender: 性别字符串
            
        Returns:
            性别枚举
        """
        if gender == "1":
            return AuthGender.MALE
        elif gender == "0":
            return AuthGender.FEMALE
        else:
            return AuthGender.UNKNOWN 