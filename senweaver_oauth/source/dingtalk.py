"""
钉钉认证源
"""
import uuid
from typing import Dict, Any, Optional

from senweaver_oauth.config import AuthConfig
from senweaver_oauth.enums.auth_scope import AuthScope
from senweaver_oauth.enums.auth_gender import AuthGender
from senweaver_oauth.enums.auth_source import AuthDefaultSource, AuthSource
from senweaver_oauth.model.auth_callback import AuthCallback
from senweaver_oauth.model.auth_response import AuthTokenResponse, AuthUserResponse
from senweaver_oauth.model.auth_token import AuthToken
from senweaver_oauth.model.auth_user import AuthUser
from senweaver_oauth.source.base import BaseAuthSource


class AuthDingtalkSource(BaseAuthSource):
    """
    钉钉认证源
    实现钉钉扫码登录
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
            source=source or AuthDefaultSource.DINGTALK
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
        return f"{url}?{query}"
        
    def get_access_token(self, callback: AuthCallback) -> AuthTokenResponse:
        """
        获取访问令牌
        
        注意：钉钉获取访问令牌的流程与其他平台略有不同
        1. 先通过authorization_code获取用户的unionid和openid
        2. 然后通过appkey和appsecret获取企业访问凭证
        
        Args:
            callback: 授权回调参数
            
        Returns:
            访问令牌响应
        """
        # 第一步：通过临时授权码获取用户身份
        temp_auth_code_url = "https://oapi.dingtalk.com/sns/getuserinfo_bycode"
        params = {
            "accessKey": self.config.client_id,
            "timestamp": str(int(self._get_timestamp() * 1000)),
            "signature": self._compute_signature()
        }
        
        post_data = {
            "tmp_auth_code": callback.code
        }
        
        response = self.http_client.post(temp_auth_code_url, params=params, json=post_data)
                    
        user_info = response
        
        if user_info.get("errcode", 0) != 0:
            return AuthTokenResponse(
                code=user_info.get("errcode", -1),
                message=user_info.get("errmsg", "获取用户身份失败")
            )
            
        # 获取用户的unionid和openid
        user_info_data = user_info.get("user_info", {})
        unionid = user_info_data.get("unionid", "")
        openid = user_info_data.get("openid", "")
        nick = user_info_data.get("nick", "")
        
        # 第二步：获取企业访问凭证
        params = {
            "appkey": self.config.client_id,
            "appsecret": self.config.client_secret
        }
        
        response = self.http_client.get(self.source.access_token_url, params=params)
        
                    
        token_info = response
        
        if token_info.get("errcode", 0) != 0:
            return AuthTokenResponse(
                code=token_info.get("errcode", -1),
                message=token_info.get("errmsg", "获取访问令牌失败")
            )
            
        # 构建令牌
        token = AuthToken(
            access_token=token_info.get("access_token", ""),
            token_type="Bearer",
            expires_in=token_info.get("expires_in", 7200),
            open_id=openid,
            union_id=unionid
        )
        
        # 缓存昵称，用于用户信息构建
        # 由于钉钉获取用户详细信息需要单独的接口和权限
        # 这里暂存用户基本信息
        self._cache_user_info(token.access_token, {
            "nick": nick, 
            "unionid": unionid,
            "openid": openid
        })
        
        return AuthTokenResponse(
            code=200,
            message="获取访问令牌成功",
            data=token
        )
        
    def get_user_info(self, token: AuthToken, **kwargs) -> AuthUserResponse:
        """
        获取用户信息
        
        钉钉API比较特殊，获取用户详情需要先获取用户的userid，
        而获取userid需要使用unionid，同时需要应用有相应的权限
        这里为了简化流程，直接返回授权过程中获取的基本信息
        
        Args:
            token: 访问令牌
            
        Returns:
            用户信息响应
        """
        # 从缓存获取用户基本信息
        cached_user_info = self._get_cached_user_info(token.access_token)
        
        if not cached_user_info:
            return AuthUserResponse(
                code=400,
                message="获取用户信息失败：无用户缓存"
            )
            
        # 构建用户对象
        user = AuthUser(
            uuid=f"{self.source.name}_{token.union_id}",
            username=cached_user_info.get("nick", ""),
            nickname=cached_user_info.get("nick", ""),
            avatar="",  # 钉钉API无法直接获取头像
            gender=AuthGender.UNKNOWN,   # 钉钉API无法直接获取性别
            email="",   # 钉钉API无法直接获取邮箱
            token=token,
            source=self.source.name,
            raw_user_info=cached_user_info
        )
        
        return AuthUserResponse(
            code=200,
            message="获取用户信息成功",
            data=user
        )
        
    def refresh_token(self, token: AuthToken) -> AuthTokenResponse:
        """
        刷新访问令牌
        钉钉不支持刷新token，需要重新获取
        
        Args:
            token: 访问令牌
            
        Returns:
            刷新后的访问令牌响应
        """
        # 获取企业访问凭证
        params = {
            "appkey": self.config.client_id,
            "appsecret": self.config.client_secret
        }
        
        response = self.http_client.get(self.source.access_token_url, params=params)
        
            
        token_info = response        
        if token_info.get("errcode", 0) != 0:
            return AuthTokenResponse(
                code=token_info.get("errcode", -1),
                message=token_info.get("errmsg", "刷新访问令牌失败")
            )
            
        # 构建新令牌
        new_token = AuthToken(
            access_token=token_info.get("access_token", ""),
            token_type="Bearer",
            expires_in=token_info.get("expires_in", 7200),
            open_id=token.open_id,  # 保留原openid
            union_id=token.union_id  # 保留原unionid
        )
        
        return AuthTokenResponse(
            code=200,
            message="刷新访问令牌成功",
            data=new_token
        )
        
    def revoke_token(self, token: AuthToken) -> bool:
        """
        撤销访问令牌
        钉钉不支持主动撤销token
        
        Args:
            token: 访问令牌
            
        Returns:
            是否成功
        """
        # 钉钉不支持主动撤销token
        return False
        
    def _compute_signature(self) -> str:
        """
        计算签名
        钉钉API需要特殊的签名计算逻辑
        
        注意：这里简化实现，实际应使用钉钉官方要求的签名算法
        
        Returns:
            签名字符串
        """
        # 实际应用中应使用HMAC-SHA256算法计算签名
        # 这里返回一个占位符
        return "signature_placeholder"
        
    def _get_timestamp(self) -> float:
        """
        获取当前时间戳
        
        Returns:
            当前时间戳（秒）
        """
        import time
        return time.time()
        
    def _cache_user_info(self, access_token: str, user_info: Dict[str, Any]) -> None:
        """
        缓存用户信息
        
        Args:
            access_token: 访问令牌
            user_info: 用户信息
        """
        # 使用AuthToken作为key存储用户信息
        cache_key = f"dingtalk_user_{access_token}"
        self.cache_store.set(cache_key, user_info)
        
    def _get_cached_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        获取缓存的用户信息
        
        Args:
            access_token: 访问令牌
            
        Returns:
            用户信息字典，如果不存在则返回None
        """
        cache_key = f"dingtalk_user_{access_token}"
        return self.cache_store.get(cache_key) 