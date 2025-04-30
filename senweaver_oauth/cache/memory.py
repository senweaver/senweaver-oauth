"""
内存缓存存储实现
"""
from typing import Any, Optional

from cachetools import TTLCache

from senweaver_oauth.cache.base import CacheStore


class MemoryCacheStore(CacheStore):
    """
    内存缓存存储实现
    """
    
    def __init__(self, maxsize: int = 1000, ttl: int = 180):
        """
        初始化
        
        Args:
            maxsize: 最大缓存数量
            ttl: 默认过期时间，单位：秒
        """
        self.ttl = ttl
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)
        
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在则返回None
        """
        return self.cache.get(key)
        
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            timeout: 过期时间，单位：秒，None表示使用默认过期时间
        """
        # 如果指定了过期时间，则使用指定的过期时间
        ttl = timeout or self.ttl
        self.cache[key] = value
        
    def delete(self, key: str) -> None:
        """
        删除缓存
        
        Args:
            key: 缓存键
        """
        if key in self.cache:
            del self.cache[key]
        
    def clear(self) -> None:
        """
        清空缓存
        """
        self.cache.clear() 