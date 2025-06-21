"""
Twitter认证源
"""
import base64
import hmac
import hashlib
from typing import Dict, Optional
from urllib.parse import parse_qsl

from senweaver_oauth.config import AuthConfig
from senweaver_oauth.enums.auth_gender import AuthGender
from senweaver_oauth.enums.auth_source import AuthDefaultSource, AuthSource
from senweaver_oauth.model.auth_callback import AuthCallback
from senweaver_oauth.model.auth_response import AuthTokenResponse, AuthUserResponse
from senweaver_oauth.model.auth_token import AuthToken
from senweaver_oauth.model.auth_user import AuthUser
from senweaver_oauth.source.base import BaseAuthSource


class AuthTwitterSource(BaseAuthSource):
    """
    Twitter认证源
    实现Twitter登录功能
    
    注意：Twitter还使用OAuth 1.0a协议，不同于其他使用OAuth 2.0的平台
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
            source=source or AuthDefaultSource.TWITTER
        )
        
    def get_authorize_params(self, state: Optional[str] = None) -> Dict[str, str]:
        """
        获取授权参数
        
        Twitter认证流程需要先获取请求令牌
        
        Args:
            state: 自定义state参数，用于防止CSRF攻击
            
        Returns:
            授权参数
        """
        # Twitter的OAuth 1.0a流程需要先获取request token
        request_token = self._get_request_token()
        
        if not request_token:
            return {}
            
        params = {
            "oauth_token": request_token.get("oauth_token", "")
        }
        
        # 缓存oauth_token_secret用于后续获取访问令牌
        if "oauth_token_secret" in request_token:
            cache_key = f"twitter_token_secret_{request_token['oauth_token']}"
            self.cache_store.set(cache_key, request_token["oauth_token_secret"])
            
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
        # 从缓存获取oauth_token_secret
        cache_key = f"twitter_token_secret_{callback.oauth_token}"
        oauth_token_secret = self.cache_store.get(cache_key)
        
        if not oauth_token_secret:
            return AuthTokenResponse(
                code=400,
                message="获取访问令牌失败: 未找到oauth_token_secret"
            )
            
        # 构建OAuth 1.0a授权头
        headers = {
            "Authorization": self._build_oauth_header(
                "POST",
                self.source.access_token_url,
                {
                    "oauth_token": callback.oauth_token,
                    "oauth_verifier": callback.oauth_verifier
                },
                oauth_token_secret
            )
        }
        
        response = self.http_client.post(
            self.source.access_token_url,
            headers=headers
        )            
        # Twitter返回文本格式的响应，需要解析
        response_data = dict(parse_qsl(response.text))
        
        token = AuthToken(
            access_token=response_data.get("oauth_token", ""),
            token_type="OAuth1.0a",
            token_secret=response_data.get("oauth_token_secret", ""),
            user_id=response_data.get("user_id", ""),
            screen_name=response_data.get("screen_name", "")
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
        # 构建OAuth 1.0a授权头
        headers = {
            "Authorization": self._build_oauth_header(
                "GET",
                self.source.user_info_url,
                {
                    "oauth_token": token.access_token,
                    "include_email": "true"  # 请求包含邮箱（需要应用有权限）
                },
                token.token_secret
            )
        }
        
        response = self.http_client.get(
            self.source.user_info_url,
            headers=headers
        )
                    
        data = response
        
        user_id = data.get("id_str", "")
        username = data.get("screen_name", "")
        nickname = data.get("name", "")
        avatar = data.get("profile_image_url_https", "").replace("_normal", "")  # 获取原始大小头像
        description = data.get("description", "")
        email = data.get("email", "")
        location = data.get("location", "")
        
        user = AuthUser(
            uuid=f"{self.source.name}_{user_id}",
            username=username,
            nickname=nickname,
            avatar=avatar,
            gender=AuthGender.UNKNOWN,  # Twitter不提供性别信息
            email=email,
            location=location,
            remark=description,
            token=token,
            source=self.source.name,
            raw_user_info=data  # 添加原始用户信息
        )
        
        return AuthUserResponse(
            code=200,
            message="获取用户信息成功",
            data=user
        )
        
    def refresh_token(self, token: AuthToken) -> AuthTokenResponse:
        """
        刷新访问令牌
        
        Twitter OAuth 1.0a不支持刷新令牌
        
        Args:
            token: 访问令牌
            
        Returns:
            刷新后的访问令牌响应
        """
        return AuthTokenResponse(
            code=400,
            message="Twitter不支持刷新访问令牌"
        )
        
    def revoke_token(self, token: AuthToken) -> bool:
        """
        撤销访问令牌
        
        Args:
            token: 访问令牌
            
        Returns:
            是否成功
        """
        # Twitter不支持通过API撤销令牌
        return False
        
    def _get_request_token(self) -> Dict[str, str]:
        """
        获取请求令牌
        
        这是OAuth 1.0a流程的第一步
        
        Returns:
            请求令牌信息
        """
        params = {
            "oauth_callback": self.config.redirect_uri
        }
        
        headers = {
            "Authorization": self._build_oauth_header(
                "POST",
                "https://api.twitter.com/oauth/request_token",
                params
            )
        }
        
        response = self.http_client.post(
            "https://api.twitter.com/oauth/request_token",
            headers=headers
        )        
            
        # 解析返回值，格式如：oauth_token=xxx&oauth_token_secret=yyy&oauth_callback_confirmed=true
        return dict(parse_qsl(response.text))
        
    def _build_oauth_header(self, method: str, url: str, params: Dict[str, str], 
                            oauth_token_secret: Optional[str] = None) -> str:
        """
        构建OAuth 1.0a授权头
        
        Args:
            method: HTTP方法
            url: 请求URL
            params: 请求参数
            oauth_token_secret: 令牌密钥
            
        Returns:
            授权头
        """
        oauth_params = {
            "oauth_consumer_key": self.config.client_id,
            "oauth_nonce": self._generate_nonce(),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(self._get_timestamp())),
            "oauth_version": "1.0"
        }
        
        # 合并参数
        all_params = {**oauth_params, **params}
        
        # 计算签名
        signature = self._generate_signature(
            method,
            url,
            all_params,
            oauth_token_secret
        )
        
        # 添加签名到参数
        all_params["oauth_signature"] = signature
        
        # 构建授权头
        auth_header = "OAuth " + ", ".join([f'{k}="{v}"' for k, v in all_params.items() if k.startswith("oauth_")])
        
        return auth_header
        
    def _generate_nonce(self) -> str:
        """
        生成随机字符串
        
        Returns:
            随机字符串
        """
        import random
        import string
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))
        
    def _get_timestamp(self) -> int:
        """
        获取当前时间戳
        
        Returns:
            当前时间戳（秒）
        """
        import time
        return time.time()
        
    def _generate_signature(self, method: str, url: str, params: Dict[str, str], 
                           oauth_token_secret: Optional[str] = None) -> str:
        """
        生成OAuth 1.0a签名
        
        Args:
            method: HTTP方法
            url: 请求URL
            params: 请求参数
            oauth_token_secret: 令牌密钥
            
        Returns:
            签名
        """
        # 参数排序
        sorted_params = sorted(params.items())
        
        # 构建参数字符串
        param_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        
        # 构建签名基础字符串
        signature_base = f"{method.upper()}&{self._url_encode(url)}&{self._url_encode(param_string)}"
        
        # 构建签名密钥
        signing_key = f"{self._url_encode(self.config.client_secret)}&"
        if oauth_token_secret:
            signing_key += self._url_encode(oauth_token_secret)
        
        # 计算签名
        signature = hmac.new(
            signing_key.encode(),
            signature_base.encode(),
            hashlib.sha1
        ).digest()
        
        # Base64编码
        return base64.b64encode(signature).decode()
        
    def _url_encode(self, text: str) -> str:
        """
        URL编码
        
        Args:
            text: 待编码文本
            
        Returns:
            编码后文本
        """
        import urllib.parse
        return urllib.parse.quote(text, safe="") 