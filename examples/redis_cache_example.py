#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Redis缓存示例
演示如何使用Redis缓存存储OAuth状态
"""

import redis
import os
import json
from typing import Any, Optional
from dotenv import load_dotenv
from senweaver_oauth import AuthRequest, AuthConfig
from senweaver_oauth.source import AuthGithubSource
from senweaver_oauth.cache.base import CacheStore
from senweaver_oauth.cache import DefaultCacheStore


# Redis缓存存储实现 - 如果需要单独使用，可以直接复制此类
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
        """获取完整的缓存键"""
        return f"{self.prefix}{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存，不存在则返回None"""
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
        """设置缓存，timeout为过期时间(秒)"""
        full_key = self._get_key(key)
        ttl = timeout if timeout is not None else self.ttl
        
        # 如果是复杂对象，则转换为JSON字符串
        if not isinstance(value, (str, int, float, bool, bytes)) and value is not None:
            value = json.dumps(value)
        
        # 设置缓存，并指定过期时间
        self.redis.set(full_key, value, ex=ttl)
    
    def delete(self, key: str) -> None:
        """删除缓存"""
        full_key = self._get_key(key)
        self.redis.delete(full_key)
    
    def clear(self) -> None:
        """清空所有以prefix开头的键"""
        keys = self.redis.keys(f"{self.prefix}*")
        if keys:
            self.redis.delete(*keys)


# 加载环境变量
load_dotenv()

def main():
    # 创建Redis客户端
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=int(os.getenv("REDIS_DB", "0")),
        password=os.getenv("REDIS_PASSWORD", None),
        decode_responses=True  # 自动将字节解码为字符串
    )
    
    try:
        # 测试Redis连接
        redis_client.ping()
        print("Redis连接成功")
        
        # 创建Redis缓存存储
        redis_cache = RedisCacheStore(
            redis_client=redis_client,
            prefix="senweaver_oauth:",  # 缓存键前缀
            ttl=300  # 默认过期时间（秒）
        )
        
        # 设置为默认缓存实例
        DefaultCacheStore.set_instance(redis_cache)
        print("已将Redis缓存设置为默认缓存实例")
        
        # 创建授权请求
        auth_config = AuthConfig(
            client_id=os.getenv("GITHUB_CLIENT_ID", "your_github_client_id"),
            client_secret=os.getenv("GITHUB_CLIENT_SECRET", "your_github_client_secret"),
            redirect_uri=os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8000/github/callback")
        )
        auth_request = AuthRequest.build(AuthGithubSource, auth_config)
        
        # 生成随机state
        import uuid
        state = str(uuid.uuid4())
        
        # 生成授权URL
        auth_url = auth_request.authorize(state)
        print(f"授权URL: {auth_url}")
        
        # 模拟将state存入Redis缓存
        print(f"State '{state}' 已存入Redis缓存")
        
        # 模拟回调处理
        print("\n----- 模拟授权回调处理 -----")
        print("当用户完成授权后，将返回带有code和state的回调URL")
        print("您需要验证state并使用code获取访问令牌")
        
        # 从Redis中检查state是否存在
        print(f"\n检查state是否在缓存中: {auth_request.check_state(state)}")
        
        # 使用特定缓存示例
        print("\n----- 使用特定缓存实例 -----")
        # 创建另一个Redis缓存实例（不同的前缀）
        another_redis_cache = RedisCacheStore(
            redis_client=redis_client,
            prefix="another_oauth:",
            ttl=600
        )
        
        # 创建使用特定缓存的授权请求
        auth_request_with_cache = AuthRequest.build(
            AuthGithubSource, 
            auth_config,
            cache_store=another_redis_cache  # 指定使用特定缓存实例
        )
        
        # 生成新的state
        another_state = str(uuid.uuid4())
        auth_url = auth_request_with_cache.authorize(another_state)
        print(f"使用特定缓存的授权URL: {auth_url}")
        print(f"State '{another_state}' 已存入特定的Redis缓存")
        
        # 测试缓存基本功能
        print("\n----- 测试缓存基本功能 -----")
        key = "test_key"
        value = {"name": "SenWeaver", "version": "0.1.0"}
        
        # 设置缓存
        redis_cache.set(key, value, 60)
        print(f"设置缓存: {key} = {value}")
        
        # 获取缓存
        cached_value = redis_cache.get(key)
        print(f"获取缓存: {key} = {cached_value}")
        
        # 删除缓存
        redis_cache.delete(key)
        print(f"删除缓存: {key}")
        
        # 验证缓存已删除
        cached_value = redis_cache.get(key)
        print(f"验证缓存已删除: {key} = {cached_value}")
        
        # 清理示例
        print("\n----- 清理缓存 -----")
        # 清理默认缓存中的state
        result = auth_request.remove_state(state)
        print(f"清理默认缓存中的state: {result}")
        
        # 清理特定缓存中的state
        result = auth_request_with_cache.remove_state(another_state)
        print(f"清理特定缓存中的state: {result}")
        
    except redis.exceptions.ConnectionError:
        print("Redis连接失败，请确保Redis服务器正在运行")
    except Exception as e:
        print(f"发生错误: {str(e)}")
    finally:
        # 关闭Redis连接
        redis_client.close()
        print("Redis连接已关闭")

if __name__ == "__main__":
    main() 