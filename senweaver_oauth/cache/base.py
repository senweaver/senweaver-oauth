"""
缓存存储接口
"""
from abc import ABC, abstractmethod
from typing import Any, Optional


class CacheStore(ABC):
    """
    缓存存储接口
    """
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在则返回None
        """
        pass
        
    @abstractmethod
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            timeout: 过期时间，单位：秒，None表示永不过期
        """
        pass
        
    @abstractmethod
    def delete(self, key: str) -> None:
        """
        删除缓存
        
        Args:
            key: 缓存键
        """
        pass
        
    @abstractmethod
    def clear(self) -> None:
        """
        清空缓存
        """
        pass 