"""
QQ认证源
"""
import re
import json
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


class AuthQqSource(BaseAuthSource):
    """
    QQ认证源
    实现QQ登录功能
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
            source=source or AuthDefaultSource.QQ
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
        
        response = self.http_client.get(self.source.access_token_url, params=params)
        
            
        # QQ的返回格式是URL参数格式，而不是JSON
        # 例如：access_token=YOUR_ACCESS_TOKEN&expires_in=7776000&refresh_token=YOUR_REFRESH_TOKEN
        result = self._parse_url_response(response.text)
        
        if "error" in result:
            return AuthTokenResponse(
                code=400,
                message=f"获取访问令牌失败: {result.get('error_description', '')}"
            )
            
        # 获取openid，QQ授权需要单独获取openid
        open_id = self._get_openid(result.get("access_token", ""))
        if not open_id:
            return AuthTokenResponse(
                code=400,
                message="获取用户OpenID失败"
            )
            
        token = AuthToken(
            access_token=result.get("access_token", ""),
            token_type="Bearer",
            expires_in=int(result.get("expires_in", "0")),
            refresh_token=result.get("refresh_token", ""),
            open_id=open_id,
            scope=result.get("scope", "")
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
            "oauth_consumer_key": self.config.client_id,
            "openid": token.open_id,
            "format": "json"
        }
        
        response = self.http_client.get(self.source.user_info_url, params=params)
        
            
        data = response
        
        if data.get("ret", 0) != 0:
            return AuthUserResponse(
                code=data.get("ret", 400),
                message=data.get("msg", "获取用户信息失败")
            )
            
        user = AuthUser(
            uuid=f"{self.source.name}_{token.open_id}",
            username=data.get("nickname", ""),
            nickname=data.get("nickname", ""),
            avatar=data.get("figureurl_qq_2", "") or data.get("figureurl_qq_1", ""),
            gender=self._get_gender(data.get("gender", "")),
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
        if not token.refresh_token:
            return AuthTokenResponse(
                code=400,
                message="刷新令牌为空"
            )
            
        params = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "refresh_token": token.refresh_token,
            "grant_type": "refresh_token"
        }
        
        response = self.http_client.get(self.source.access_token_url, params=params)
        
                    
        # QQ的返回格式是URL参数格式
        result = self._parse_url_response(response.text)
        
        if "error" in result:
            return AuthTokenResponse(
                code=400,
                message=f"刷新访问令牌失败: {result.get('error_description', '')}"
            )
            
        # QQ刷新token后，openid不会改变
        token = AuthToken(
            access_token=result.get("access_token", ""),
            token_type="Bearer",
            expires_in=int(result.get("expires_in", "0")),
            refresh_token=result.get("refresh_token", ""),
            open_id=token.open_id,  # 复用原来的openid
            scope=result.get("scope", "")
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
        # QQ登录不支持撤销访问令牌
        return False
        
    def _parse_url_response(self, text: str) -> Dict[str, str]:
        """
        解析URL参数格式的响应
        
        Args:
            text: 响应文本
            
        Returns:
            解析后的结果
        """
        result = {}
        if text.startswith("callback("):
            # 针对JSONP格式的处理
            match = re.search(r'callback\((.*)\);', text)
            if match:
                try:
                    result = json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
        else:
            # 标准的URL参数格式处理
            parts = text.split("&")
            for part in parts:
                if "=" in part:
                    key, value = part.split("=", 1)
                    result[key] = value
                    
        return result
        
    def _get_openid(self, access_token: str) -> str:
        """
        获取QQ用户的OpenID
        
        Args:
            access_token: 访问令牌
            
        Returns:
            OpenID
        """
        if not access_token:
            return ""
            
        # QQ获取OpenID的接口
        url = "https://graph.qq.com/oauth2.0/me"
        params = {
            "access_token": access_token,
            "fmt": "json"  # 指定返回格式为JSON
        }
        
        response = self.http_client.get(url, params=params)
                    
        try:
            data = response
            return data.get("openid", "")
        except json.JSONDecodeError:
            # 尝试解析非JSON格式的响应
            match = re.search(r'"openid":"([^"]+)"', response.text)
            if match:
                return match.group(1)
            return ""
            
    def _get_gender(self, gender: str) -> AuthGender:
        """
        转换性别编码
        
        Args:
            gender: 性别字符串，QQ返回的是"男"/"女"
            
        Returns:
            性别整数，0: 未知, 1: 男, 2: 女
        """
        if gender == "男":
            return AuthGender.MALE
        elif gender == "女":
            return AuthGender.FEMALE
        else:
            return AuthGender.UNKNOWN