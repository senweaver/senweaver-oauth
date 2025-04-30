# 缓存存储使用指南

SenWeaver OAuth提供了多种缓存存储实现，用于存储OAuth认证过程中的状态和令牌信息。本文档介绍如何使用不同的缓存存储实现。

## 可用的缓存存储

SenWeaver OAuth内置了以下缓存存储实现：

1. **MemoryCacheStore**: 默认的内存缓存存储，适用于单实例应用。
2. **RedisCacheStore**: Redis缓存存储，适用于分布式应用或需要持久化缓存的场景。

## 默认缓存存储

默认情况下，SenWeaver OAuth使用`MemoryCacheStore`作为缓存存储。您可以通过`DefaultCacheStore`获取全局缓存实例：

```python
from senweaver_oauth.cache import DefaultCacheStore

# 获取全局缓存实例
cache = DefaultCacheStore.get_instance()

# 使用缓存
cache.set("key", "value", 300)  # 300秒后过期
value = cache.get("key")
```

## 使用Redis缓存存储

如果您的应用需要在多个实例间共享缓存，或需要持久化缓存数据，可以使用Redis缓存存储：

```python
import redis
from senweaver_oauth.cache import RedisCacheStore, DefaultCacheStore

# 创建Redis客户端
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    password=None,
    decode_responses=False  # 保持原始二进制数据，让RedisCacheStore处理解码
)

# 创建Redis缓存存储
redis_cache = RedisCacheStore(
    redis_client=redis_client,
    prefix="senweaver_oauth:",  # 缓存键前缀
    ttl=300  # 默认过期时间（秒）
)

# 设置为默认缓存实例
DefaultCacheStore.set_instance(redis_cache)
```

设置为默认缓存实例后，SenWeaver OAuth的所有操作将使用Redis缓存。

## 自定义缓存存储

您还可以实现自己的缓存存储，只需继承`CacheStore`接口并实现所有抽象方法：

```python
from senweaver_oauth.cache import CacheStore, DefaultCacheStore
from typing import Any, Optional

class CustomCacheStore(CacheStore):
    """
    自定义缓存存储实现
    """
    
    def get(self, key: str) -> Optional[Any]:
        # 实现获取缓存的逻辑
        pass
        
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        # 实现设置缓存的逻辑
        pass
        
    def delete(self, key: str) -> None:
        # 实现删除缓存的逻辑
        pass
        
    def clear(self) -> None:
        # 实现清空缓存的逻辑
        pass

# 设置为默认缓存实例
custom_cache = CustomCacheStore()
DefaultCacheStore.set_instance(custom_cache)
```

## 在OAuth认证请求中使用特定缓存

您也可以为特定的OAuth认证请求指定使用的缓存存储，而不影响全局缓存设置：

```python
from senweaver_oauth import AuthConfig, AuthRequest
from senweaver_oauth.cache import RedisCacheStore

# 创建Redis缓存存储
redis_cache = RedisCacheStore(redis_client)

# 创建认证配置
auth_config = AuthConfig(
    client_id="your_client_id",
    client_secret="your_client_secret",
    redirect_uri="your_redirect_uri"
)

# 创建认证请求，并指定使用Redis缓存
auth_request = AuthRequest(
    "github",
    auth_config,
    cache_store=redis_cache
)
```

这样，即使全局缓存使用的是内存缓存，这个特定的认证请求也会使用Redis缓存。

## 注意事项

- 对于生产环境，建议使用Redis缓存存储，以便在分布式环境中共享缓存数据。
- 在使用Redis缓存时，请确保Redis服务器的安全配置，避免缓存数据泄露。
- 缓存过期时间应根据实际需求设置，OAuth状态通常只需要几分钟的有效期。 