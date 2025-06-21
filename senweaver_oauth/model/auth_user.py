"""
用户信息模型
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

from senweaver_oauth.enums.auth_gender import AuthGender
from senweaver_oauth.model.auth_token import AuthToken


@dataclass
class AuthUser:
    """
    第三方平台用户信息
    """
    uuid: str  # 用户第三方平台的唯一id
    username: str  # 用户名
    nickname: Optional[str] = None  # 昵称
    avatar: Optional[str] = None  # 头像
    blog: Optional[str] = None  # 网址
    company: Optional[str] = None  # 所在公司
    location: Optional[str] = None  # 位置
    email: Optional[str] = None  # 邮箱
    mobile: Optional[str] = None  # 手机号
    remark: Optional[str] = None  # 用户备注
    gender: Optional[AuthGender] = AuthGender.UNKNOWN  # 性别
    source: Optional[str] = None  # 来源平台
    token: Optional[AuthToken] = None  # token信息
    raw_user_info: Optional[Dict[str, Any]] = field(default_factory=dict)  # 原始用户信息
    service_url:Optional[str] = None # 部门平台需要重定向的服务地址

    def __str__(self) -> str:
        return f"AuthUser(uuid={self.uuid}, username={self.username}, source={self.source})"
        
    def __repr__(self) -> str:
        return self.__str__() 