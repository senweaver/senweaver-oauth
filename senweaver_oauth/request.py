"""
认证请求类
"""
from typing import Dict, Any, Optional, Type

from senweaver_oauth.config import AuthConfig
from senweaver_oauth.model.auth_response import AuthUserResponse
from senweaver_oauth.source.base import BaseAuthSource


class AuthRequest:
    """
    认证请求类
    """
    
    def __init__(self, auth_source: BaseAuthSource):
        """
        初始化
        
        Args:
            auth_source: 认证源实例
        """
        self.auth_source = auth_source
        
    def authorize(self, state: Optional[str] = None, **kwargs) -> str:
        """
        生成授权URL
        
        Args:
            state: 自定义state参数，用于防止CSRF攻击
            
        Returns:
            授权URL
        """
        return self.auth_source.authorize(state, **kwargs)
        
    def login(self, callback: Dict[str, Any], **kwargs) -> AuthUserResponse:
        """
        登录
        
        Args:
            callback: 回调参数
            
        Returns:
            用户信息
        """
        return self.auth_source.login(callback, **kwargs)
        
    def refresh(self, token: str) -> AuthUserResponse:
        """
        刷新访问令牌
        
        Args:
            token: 刷新令牌
            
        Returns:
            新的访问令牌
        """
        return self.auth_source.refresh(token)
        
    def revoke(self, token: str) -> AuthUserResponse:
        """
        撤销访问令牌
        
        Args:
            token: 访问令牌
            
        Returns:
            撤销结果
        """
        return self.auth_source.revoke(token)
        
    @classmethod
    def build(cls, auth_source_class: Type[BaseAuthSource], config: AuthConfig) -> 'AuthRequest':
        """
        构建认证请求
        
        Args:
            auth_source_class: 认证源类
            config: 认证配置
            
        Returns:
            认证请求实例
        """
        auth_source = auth_source_class(config)
        return cls(auth_source) 