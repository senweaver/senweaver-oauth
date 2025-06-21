"""
微信开放平台认证源
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


class AuthWechatOpenSource(BaseAuthSource):
    """
    微信开放平台认证源
    实现PC端扫码登录
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
            source=source or AuthDefaultSource.WECHAT_OPEN
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
            "appid": self.config.client_id,
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
        
        # 微信开放平台的特殊处理，需要添加 #wechat_redirect
        return f"{url}?{query}#wechat_redirect"
        
    def get_access_token(self, callback: AuthCallback) -> AuthTokenResponse:
        """
        获取访问令牌
        
        Args:
            callback: 授权回调参数
            
        Returns:
            访问令牌响应
        """
        params = {
            "appid": self.config.client_id,
            "secret": self.config.client_secret,
            "code": callback.code,
            "grant_type": "authorization_code"
        }
        
        response = self.http_client.get(self.source.access_token_url, params=params)
                    
        data = response
        
        if "errcode" in data and data["errcode"] != 0:
            return AuthTokenResponse(
                code=data.get("errcode", -1),
                message=data.get("errmsg", "获取访问令牌失败")
            )
            
        token = AuthToken(
            access_token=data.get("access_token", ""),
            token_type="Bearer",
            expires_in=data.get("expires_in", 0),
            refresh_token=data.get("refresh_token", ""),
            open_id=data.get("openid", ""),
            union_id=data.get("unionid", ""),
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
            "openid": token.open_id,
            "lang": "zh_CN"
        }
        
        response = self.http_client.get(self.source.user_info_url, params=params)
                    
        data = response
        
        if "errcode" in data and data["errcode"] != 0:
            return AuthUserResponse(
                code=data.get("errcode", -1),
                message=data.get("errmsg", "获取用户信息失败")
            )
            
        user = AuthUser(
            uuid=f"{self.source.name}_{token.open_id}",
            username=data.get("nickname", ""),
            nickname=data.get("nickname", ""),
            avatar=data.get("headimgurl", ""),
            gender=self._get_gender(data.get("sex", "1")),
            email="",
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
        if not self.source.refresh_token_url or not token.refresh_token:
            return AuthTokenResponse(
                code=400,
                message="不支持刷新访问令牌"
            )
            
        params = {
            "appid": self.config.client_id,
            "grant_type": "refresh_token",
            "refresh_token": token.refresh_token
        }
        
        response = self.http_client.get(self.source.refresh_token_url, params=params)
            
        data = response
        
        if "errcode" in data and data["errcode"] != 0:
            return AuthTokenResponse(
                code=data.get("errcode", -1),
                message=data.get("errmsg", "刷新访问令牌失败")
            )
            
        token = AuthToken(
            access_token=data.get("access_token", ""),
            token_type="Bearer",
            expires_in=data.get("expires_in", 0),
            refresh_token=data.get("refresh_token", ""),
            open_id=data.get("openid", ""),
            union_id=data.get("unionid", ""),
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
        # 微信开放平台不支持撤销访问令牌
        return False
        
    def _get_gender(self, gender_code: str) -> AuthGender:
        """
        转换性别编码
        
        Args:
            gender_code: 性别编码
            
        Returns:
            性别枚举
        """
        if gender_code == "1":
            return AuthGender.MALE
        elif gender_code == "2":
            return AuthGender.FEMALE
        else:
            return AuthGender.UNKNOWN 