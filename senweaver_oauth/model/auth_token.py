"""
Token信息模型
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class AuthToken:
    """
    Token信息
    """
    access_token: str  # 访问令牌
    token_type: str  # 令牌类型
    expires_in: int  # 过期时间，单位：秒
    refresh_token: Optional[str] = None  # 刷新令牌
    uid: Optional[str] = None  # 用户ID
    open_id: Optional[str] = None  # 用户在第三方平台的唯一ID
    access_code: Optional[str] = None  # 访问码，部分平台返回
    union_id: Optional[str] = None  # 用户在第三方平台的唯一ID，部分平台返回
    scope: Optional[str] = None  # 权限范围
    id_token: Optional[str] = None  # 身份令牌，部分平台返回
    mac_key: Optional[str] = None  # MAC密钥，部分平台返回
    mac_algorithm: Optional[str] = None  # MAC算法，部分平台返回
    code: Optional[str] = None  # 授权码
    oauth_token: Optional[str] = None  # 用于部分平台的oauth_token参数
    oauth_token_secret: Optional[str] = None  # 用于部分平台的oauth_token_secret参数
    create_time: datetime = field(default_factory=datetime.now)  # 创建时间
    extras: Dict[str, Any] = field(default_factory=dict)  # 扩展信息

    @property
    def expired(self) -> bool:
        """
        判断token是否过期
        
        Returns:
            是否过期
        """
        if self.expires_in is None or self.expires_in <= 0:
            # 过期时间为空或者小于等于0，默认不过期
            return False
        
        # 当前时间 > 创建时间 + 过期时间，则表示已过期
        return datetime.now() > self.create_time.timestamp() + self.expires_in 