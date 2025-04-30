"""
HTTP配置
"""
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class HttpConfig:
    """
    HTTP配置
    """
    timeout: int = 10  # 超时时间，单位：秒
    proxy: Optional[Dict[str, str]] = None  # 代理配置
    verify_ssl: bool = True  # 是否验证SSL证书
    headers: Dict[str, str] = field(default_factory=dict)  # 请求头
    
    def __post_init__(self):
        """
        初始化后的处理
        """
        # 默认添加User-Agent
        if 'User-Agent' not in self.headers:
            self.headers['User-Agent'] = 'SenWeaver-OAuth' 