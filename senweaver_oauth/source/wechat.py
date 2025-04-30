"""
微信公众号认证源
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


class AuthWechatSource(BaseAuthSource):
    """
    微信公众号认证源
    实现微信移动端登录功能
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
            source=source or AuthDefaultSource.WECHAT
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
        return f"{url}?{query}#wechat_redirect"  # 微信特殊处理
        
    def get_access_token(self, callback: AuthCallback) -> AuthTokenResponse:
        """
        获取访问令牌
        
        Args:
            callback: 授权回调参数
            
        Returns:
            访问令牌响应
        """
        # 参数校验
        if not callback.code:
            return AuthTokenResponse(
                code=400,
                message="授权码不能为空"
            )
            
        # 准备请求参数
        params = {
            "appid": self.config.client_id,
            "secret": self.config.client_secret,
            "code": callback.code,
            "grant_type": "authorization_code"
        }
        
        # 发送请求
        response = self.http_client.get(self.source.access_token_url, params=params)
        
        # 微信返回结果特殊处理
        if "errcode" in response and response.get("errcode") != 0:
            return AuthTokenResponse(
                code=response.get("errcode", 400),
                message=response.get("errmsg", "获取访问令牌失败")
            )
            
        # 构建令牌对象
        token = AuthToken(
            access_token=response.get("access_token", ""),
            token_type="Bearer",
            expires_in=response.get("expires_in", 0),
            refresh_token=response.get("refresh_token", ""),
            scope=None,
            uid=response.get("openid", ""),
            open_id = response.get("openid",""),
            union_id=response.get("unionid", "")
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
        # 参数校验
        if not token or not token.access_token or not token.uid:
            return AuthUserResponse(
                code=400,
                message="访问令牌或用户标识不能为空"
            )
            
        # 准备请求参数
        params = {
            "access_token": token.access_token,
            "openid": token.uid,
            "lang": "zh_CN"
        }
        
        # 发送请求
        response = self.http_client.get(self.source.user_info_url, params=params)
        
        # 微信返回结果特殊处理
        if "errcode" in response and response.get("errcode") != 0:
            return AuthUserResponse(
                code=response.get("errcode", 400),
                message=response.get("errmsg", "获取用户信息失败")
            )
            
        # 解析用户信息
        user = AuthUser(
            uuid=f"{self.source.name}_{token.uid}",
            username=response.get("nickname", ""),
            nickname=response.get("nickname", ""),
            avatar=response.get("headimgurl", ""),
            gender=self._get_gender(response.get("sex", "")),
            location=f"{response.get('country', '')} {response.get('province', '')} {response.get('city', '')}".strip(),
            token=token,
            source=self.source.name,
            raw_user_info=response
        )
        
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
        # 参数校验
        if not refresh_token:
            return AuthTokenResponse(
                code=400,
                message="刷新令牌不能为空"
            )
            
        # 准备请求参数
        params = {
            "appid": self.config.client_id,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        # 发送请求
        response = self.http_client.get(self.source.refresh_token_url, params=params)
        
        # 微信返回结果特殊处理
        if "errcode" in response and response.get("errcode") != 0:
            return AuthTokenResponse(
                code=response.get("errcode", 400),
                message=response.get("errmsg", "刷新访问令牌失败")
            )
            
        # 构建令牌对象
        token = AuthToken(
            access_token=response.get("access_token", ""),
            token_type="Bearer",
            expires_in=response.get("expires_in", 0),
            refresh_token=response.get("refresh_token", refresh_token),
            scope=None,
            uid=response.get("openid", ""),
            union_id=response.get("unionid", "")
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
        # 微信公众号不支持撤销访问令牌
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