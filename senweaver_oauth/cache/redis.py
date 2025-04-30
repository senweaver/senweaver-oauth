"""
Redis缓存存储实现
"""
import json
from typing import Any, Optional

from senweaver_oauth.cache.base import CacheStore


class RedisCacheStore(CacheStore):
    """
    Redis缓存存储实现
    
    使用Redis作为缓存存储，支持过期时间
    """
    
    def __init__(self, redis_client, prefix: str = "senweaver:", ttl: int = 180):
        """
        初始化
        
        Args:
            redis_client: Redis客户端实例
            prefix: 缓存键前缀，用于区分不同应用的缓存
            ttl: 默认过期时间，单位：秒
        """
        self.redis = redis_client
        self.prefix = prefix
        self.ttl = ttl
    
    def _get_key(self, key: str) -> str:
        """
        获取完整的缓存键
        
        Args:
            key: 缓存键
            
        Returns:
            完整的缓存键
        """
        return f"{self.prefix}{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在则返回None
        """
        full_key = self._get_key(key)
        value = self.redis.get(full_key)
        
        if value is None:
            return None
        
        try:
            # 尝试解析为JSON
            return json.loads(value)
        except (TypeError, json.JSONDecodeError):
            # 如果不是JSON，则返回原始值
            if isinstance(value, bytes):
                return value.decode('utf-8')
            return value
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            timeout: 过期时间，单位：秒，None表示使用默认过期时间
        """
        full_key = self._get_key(key)
        ttl = timeout if timeout is not None else self.ttl
        
        # 如果是复杂对象，则转换为JSON字符串
        if not isinstance(value, (str, int, float, bool, bytes)) and value is not None:
            value = json.dumps(value)
        
        # 设置缓存，并指定过期时间
        self.redis.set(full_key, value, ex=ttl)
    
    def delete(self, key: str) -> None:
        """
        删除缓存
        
        Args:
            key: 缓存键
        """
        full_key = self._get_key(key)
        self.redis.delete(full_key)
    
    def clear(self) -> None:
        """
        清空缓存
        
        注意：此方法会清空所有以prefix开头的键
        """
        keys = self.redis.keys(f"{self.prefix}*")
        if keys:
            self.redis.delete(*keys) 