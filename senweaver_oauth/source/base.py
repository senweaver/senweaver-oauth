"""
基础认证源
"""
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from senweaver_oauth.cache.base import CacheStore
from senweaver_oauth.cache.default import DefaultCacheStore
from senweaver_oauth.config import AuthConfig
from senweaver_oauth.enums.auth_scope import AuthScope
from senweaver_oauth.enums.auth_source import AuthSource
from senweaver_oauth.http.http_client import HttpClient
from senweaver_oauth.http.requests_http_client import RequestsHttpClient
from senweaver_oauth.model.auth_callback import AuthCallback
from senweaver_oauth.model.auth_response import AuthTokenResponse, AuthUserResponse
from senweaver_oauth.model.auth_token import AuthToken


class BaseAuthSource(ABC):
    """
    基础认证源
    """
    
    def __init__(self, config: AuthConfig, source: AuthSource,
                 http_client: Optional[HttpClient] = None,
                 cache_store: Optional[CacheStore] = None):
        """
        初始化
        
        Args:
            config: 认证配置
            source: 认证源
            http_client: HTTP客户端
            cache_store: 缓存存储
        """
        self.config = config
        self.source = source
        self.http_client = http_client or RequestsHttpClient()
        self.cache_store = cache_store or DefaultCacheStore.get_instance()
        
    def authorize(self, state: Optional[str] = None,**kwargs) -> str:
        """
        生成授权URL
        
        Args:
            state: 自定义state参数，用于防止CSRF攻击
            
        Returns:
            授权URL
        """
        # 生成随机state参数
        if not state:
            state = str(uuid.uuid4())
            
        # 缓存state参数，默认有效期3分钟
        self.cache_store.set(state, state, 180)
        # 构建授权参数
        params = self.get_authorize_params(state)
        # 生成授权URL
        return self.build_authorize_url(params)
        
    def login(self, callback: Dict[str, Any], **kwargs) -> AuthUserResponse:
        """
        登录
        
        Args:
            callback: 回调参数
            **kwargs: 额外参数，将传递给get_user_info
            
        Returns:
            用户信息
        """
        # 使用AuthCallback的build方法创建对象
        callback_params = AuthCallback.build(callback)
        
        # 检查state参数，防止CSRF攻击
        if not self.config.ignore_check_state and callback_params.state:
            state = self.cache_store.get(callback_params.state)
            if not state:
                return AuthUserResponse.failure("state参数不匹配或已过期，请重新授权")
        
        # 获取访问令牌
        token_response = self.get_access_token(callback_params)
        if token_response.code != 200:
            return AuthUserResponse(
                code=token_response.code,
                status=token_response.status,
                message=token_response.message
            )
            
        # 获取用户信息，传递额外参数
        return self.get_user_info(token_response.data, **kwargs)
        
    def refresh(self, token: str) -> AuthTokenResponse:
        """
        刷新访问令牌
        
        Args:
            token: 刷新令牌
            
        Returns:
            新的访问令牌
        """
        return self.refresh_token(token)
        
    def revoke(self, token: str) -> AuthTokenResponse:
        """
        撤销访问令牌
        
        Args:
            token: 访问令牌
            
        Returns:
            撤销结果
        """
        return self.revoke_token(token)
        
    def get_scopes(self) -> str:
        """
        获取授权范围字符串        
            
        Returns:
            授权范围字符串
        """
        if self.config.scope:
            return self.config.scope
        return AuthScope.get_scope_str(self.source.name, self.source.scope_delimiter)
        
    def get_authorize_params(self, state: Optional[str] = None) -> Dict[str, Any]:
        """
        获取授权参数
        
        Args:
            state: 自定义state参数
            
        Returns:
            授权参数
        """       
        # 生成随机state参数
        if not state:
            state = str(uuid.uuid4())
            
        # 缓存state参数，默认有效期3分钟
        self.cache_store.set(state, state, 180)
        
        # 获取默认scope
        scope = self.get_scopes()
            
        params = {
            'response_type': 'code',
            'client_id': self.config.client_id,
            'redirect_uri': self.config.redirect_uri,
            'state': state
        }
        
        # 如果scope不为空，则添加到参数中
        if scope:
            params['scope'] = scope
            
        return params
        
    def build_authorize_url(self, params: Dict[str, Any]) -> str:
        """
        构建授权URL
        
        Args:
            params: 授权参数
            
        Returns:
            授权URL
        """
        # 将参数拼接到URL中
        query_str = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.source.authorize_url}?{query_str}"
    
    @abstractmethod
    def get_access_token(self, callback: AuthCallback) -> AuthTokenResponse:
        """
        获取访问令牌
        
        Args:
            callback: 回调参数
            
        Returns:
            访问令牌
        """
        pass
        
    @abstractmethod
    def get_user_info(self, token: AuthToken, **kwargs) -> AuthUserResponse:
        """
        获取用户信息
        
        Args:
            token: 访问令牌
            **kwargs: 额外参数，便于子类扩展
            
        Returns:
            用户信息
        """
        pass
        
    def refresh_token(self, refresh_token: str) -> AuthTokenResponse:
        """
        刷新访问令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            新的访问令牌
        """
        # 默认实现，如果平台不支持刷新令牌，则返回未实现
        return AuthTokenResponse.not_implemented("该平台不支持刷新令牌")
        
    def revoke_token(self, access_token: str) -> AuthTokenResponse:
        """
        撤销访问令牌
        
        Args:
            access_token: 访问令牌
            
        Returns:
            撤销结果
        """
        # 默认实现，如果平台不支持撤销令牌，则返回未实现
        return AuthTokenResponse.not_implemented("该平台不支持撤销令牌") 