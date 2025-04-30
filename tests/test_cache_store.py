"""
缓存存储测试用例
"""
import unittest
import time
from unittest.mock import patch

from senweaver_oauth.cache.memory import MemoryCacheStore
from senweaver_oauth.cache.default import DefaultCacheStore


class TestMemoryCacheStore(unittest.TestCase):
    """
    MemoryCacheStore测试用例
    """
    
    def setUp(self):
        """
        测试前准备
        """
        self.cache_store = MemoryCacheStore(maxsize=10, ttl=1)
        
    def test_set_and_get(self):
        """
        测试set和get方法
        """
        # 设置缓存
        self.cache_store.set("test_key", "test_value")
        
        # 获取缓存
        value = self.cache_store.get("test_key")
        
        # 验证结果
        self.assertEqual(value, "test_value")
        
    def test_get_with_nonexistent_key(self):
        """
        测试获取不存在的键
        """
        value = self.cache_store.get("nonexistent_key")
        self.assertIsNone(value)
        
    def test_delete(self):
        """
        测试delete方法
        """
        # 设置缓存
        self.cache_store.set("test_key", "test_value")
        
        # 删除缓存
        self.cache_store.delete("test_key")
        
        # 获取缓存
        value = self.cache_store.get("test_key")
        
        # 验证结果
        self.assertIsNone(value)
        
    def test_clear(self):
        """
        测试clear方法
        """
        # 设置多个缓存
        self.cache_store.set("test_key1", "test_value1")
        self.cache_store.set("test_key2", "test_value2")
        
        # 清空缓存
        self.cache_store.clear()
        
        # 获取缓存
        value1 = self.cache_store.get("test_key1")
        value2 = self.cache_store.get("test_key2")
        
        # 验证结果
        self.assertIsNone(value1)
        self.assertIsNone(value2)
        
    def test_expiration(self):
        """
        测试过期功能
        """
        # 设置缓存，过期时间为1秒
        self.cache_store.set("test_key", "test_value")
        
        # 立即获取缓存
        value1 = self.cache_store.get("test_key")
        self.assertEqual(value1, "test_value")
        
        # 等待2秒，确保缓存过期
        time.sleep(2)
        
        # 再次获取缓存
        value2 = self.cache_store.get("test_key")
        self.assertIsNone(value2)
        
    def test_custom_expiration(self):
        """
        测试自定义过期时间
        """
        # 设置缓存，自定义过期时间为3秒
        self.cache_store.set("test_key", "test_value", timeout=3)
        
        # 立即获取缓存
        value1 = self.cache_store.get("test_key")
        self.assertEqual(value1, "test_value")
        
        # 等待2秒，缓存不应该过期
        time.sleep(2)
        
        # 再次获取缓存
        value2 = self.cache_store.get("test_key")
        self.assertEqual(value2, "test_value")


class TestDefaultCacheStore(unittest.TestCase):
    """
    DefaultCacheStore测试用例
    """
    
    def tearDown(self):
        """
        测试后清理
        """
        DefaultCacheStore._instance = None
        
    def test_get_instance(self):
        """
        测试get_instance方法
        """
        # 获取实例
        instance = DefaultCacheStore.get_instance()
        
        # 验证结果
        self.assertIsNotNone(instance)
        self.assertIsInstance(instance, MemoryCacheStore)
        
    def test_set_instance(self):
        """
        测试set_instance方法
        """
        # 创建模拟对象
        mock_instance = unittest.mock.MagicMock()
        
        # 设置实例
        DefaultCacheStore.set_instance(mock_instance)
        
        # 获取实例
        instance = DefaultCacheStore.get_instance()
        
        # 验证结果
        self.assertIs(instance, mock_instance)
        
    def test_singleton_pattern(self):
        """
        测试单例模式
        """
        # 获取实例
        instance1 = DefaultCacheStore.get_instance()
        instance2 = DefaultCacheStore.get_instance()
        
        # 验证结果
        self.assertIs(instance1, instance2)


if __name__ == "__main__":
    unittest.main() 