"""
AuthConfig - OAuth认证配置类
"""
from dataclasses import dataclass, field
from typing import Dict, Optional, Any


@dataclass
class AuthConfig:
    """
    OAuth认证配置类
    """
    client_id: str
    client_secret: str
    redirect_uri: Optional[str] = None
    public_key: Optional[str] = None
    scope: Optional[str] = None
    state: Optional[str] = None
    ignore_check_state: bool = False
    user_info_endpoint: Optional[str] = None
    access_token_endpoint: Optional[str] = None
    refresh_token_endpoint: Optional[str] = None
    extras: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """
        初始化后的处理
        """
        if not self.client_id:
            raise ValueError("client_id不能为空")
        if not self.client_secret:
            raise ValueError("client_secret不能为空")