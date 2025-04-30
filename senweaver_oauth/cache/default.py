"""
默认缓存存储
"""
from typing import Optional

from senweaver_oauth.cache.base import CacheStore
from senweaver_oauth.cache.memory import MemoryCacheStore


class DefaultCacheStore:
    """
    默认缓存存储
    提供一个全局的缓存存储实例
    """
    # 默认缓存实例
    _instance: Optional[CacheStore] = None
    
    @classmethod
    def get_instance(cls) -> CacheStore:
        """
        获取缓存实例
        
        Returns:
            缓存实例
        """
        if cls._instance is None:
            cls._instance = MemoryCacheStore()
        return cls._instance
        
    @classmethod
    def set_instance(cls, instance: CacheStore) -> None:
        """
        设置缓存实例
        
        Args:
            instance: 缓存实例
        """
        cls._instance = instance 