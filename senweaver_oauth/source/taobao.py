"""
淘宝认证源
"""
import uuid
from typing import Dict, Optional
from urllib.parse import urlencode

from senweaver_oauth.config import AuthConfig
from senweaver_oauth.enums.auth_gender import AuthGender
from senweaver_oauth.enums.auth_source import AuthDefaultSource, AuthSource
from senweaver_oauth.model.auth_callback import AuthCallback
from senweaver_oauth.model.auth_response import AuthTokenResponse, AuthUserResponse
from senweaver_oauth.model.auth_token import AuthToken
from senweaver_oauth.model.auth_user import AuthUser
from senweaver_oauth.source.base import BaseAuthSource


class AuthTaobaoSource(BaseAuthSource):
    """
    淘宝认证源
    实现淘宝登录功能
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
            source=source or AuthDefaultSource.TAOBAO
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
            "view": "web",  # web页面视图
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
        query = urlencode(params)
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
            "grant_type": "authorization_code",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": callback.code,
            "redirect_uri": self.config.redirect_uri,
            "view": "web"
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
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
            open_id=data.get("taobao_user_id", ""),
            union_id=data.get("taobao_open_uid", ""),
            user_nick=data.get("taobao_user_nick", "")
        )
        
        # 保存昵称，因为获取用户信息可能需要单独的接口和签名
        if token.user_nick:
            cache_key = f"taobao_user_nick_{token.open_id}"
            self.cache_store.set(cache_key, token.user_nick)
        
        return AuthTokenResponse(
            code=200,
            message="获取访问令牌成功",
            data=token
        )
        
    def get_user_info(self, token: AuthToken, **kwargs) -> AuthUserResponse:
        """
        获取用户信息
        
        淘宝API调用比较复杂，需要签名以及特定的API接口权限
        这里使用访问令牌中携带的用户信息来构建用户对象
        实际应用中，如果需要更多的用户信息，需要调用淘宝的API接口
        
        Args:
            token: 访问令牌
            
        Returns:
            用户信息响应
        """
        # 从缓存获取用户昵称
        cache_key = f"taobao_user_nick_{token.open_id}"
        user_nick = self.cache_store.get(cache_key) or token.user_nick or ""
        
        # 构建用户信息
        user = AuthUser(
            uuid=f"{self.source.name}_{token.open_id}",
            username=user_nick,
            nickname=user_nick,
            avatar="",  # 淘宝API不直接提供头像
            gender=AuthGender.UNKNOWN,   # 淘宝API不直接提供性别
            email="",   # 淘宝API不直接提供邮箱
            token=token,
            source=self.source.name,
            raw_user_info={"user_nick": user_nick, "open_id": token.open_id, "union_id": token.union_id}
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
        if not token.refresh_token:
            return AuthTokenResponse(
                code=400,
                message="不支持刷新访问令牌"
            )
            
        params = {
            "grant_type": "refresh_token",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "refresh_token": token.refresh_token
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
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
                message=f"刷新访问令牌失败: {data.get('error_description', data.get('error', ''))}"
            )
            
        new_token = AuthToken(
            access_token=data.get("access_token", ""),
            token_type="Bearer",
            expires_in=data.get("expires_in", 0),
            refresh_token=data.get("refresh_token", token.refresh_token),
            open_id=data.get("taobao_user_id", token.open_id),
            union_id=data.get("taobao_open_uid", token.union_id),
            user_nick=data.get("taobao_user_nick", token.user_nick)
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
        # 淘宝不支持撤销令牌
        return False 