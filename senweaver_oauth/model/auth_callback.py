"""
授权回调参数
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, ClassVar


@dataclass
class AuthCallback:
    """
    授权回调参数
    """
    code: Optional[str] = None  # 授权码，授权成功后，平台返回的授权码
    auth_code: Optional[str] = None  # 授权码，支付宝专用
    state: Optional[str] = None  # 状态码，用于和请求时的state参数比较，防止CSRF攻击
    authorization_code: Optional[str] = None
    oauth_token: Optional[str] = None
    oauth_verifier: Optional[str] = None
    user: Optional[str] = None
    error: Optional[str] = None  # 错误码
    error_description: Optional[str] = None  # 错误描述
    error_uri: Optional[str] = None  # 错误页面URI
    extras: Dict[str, Any] = field(default_factory=dict)  # 扩展参数
    
    # 已知字段集合，用于识别哪些是类的字段
    _known_fields: ClassVar[set] = None
    
    def __post_init__(self):
        """
        初始化后的处理
        说明：部分平台的授权回调参数不一致，需要转换
        """
        # 优先使用code，如果code为空则使用auth_code（支付宝）
        if not self.code and self.auth_code:
            self.code = self.auth_code
    
    @classmethod
    def build(cls, data: Dict[str, Any]) -> 'AuthCallback':
        """
        构建AuthCallback对象
        
        Args:
            data: 回调参数字典
            
        Returns:
            AuthCallback对象
        """
        # 初始化已知字段集合
        if cls._known_fields is None:
            # 去掉extras字段，它用于存储未知字段
            cls._known_fields = set(cls.__annotations__.keys()) - {'extras'}
        
        # 一次遍历处理所有字段
        kwargs = {}
        extras = {}
        
        for k, v in data.items():
            if k in cls._known_fields:
                kwargs[k] = v
            else:
                extras[k] = v
                
        # 添加extras字段（如果有）
        if extras:
            kwargs['extras'] = extras
            
        return cls(**kwargs) 