"""
AuthConfig测试用例
"""
import unittest
import pytest
from senweaver_oauth.config import AuthConfig


class TestAuthConfig(unittest.TestCase):
    """
    AuthConfig测试用例
    """
    
    def test_create_auth_config(self):
        """
        测试创建AuthConfig对象
        """
        # 创建AuthConfig对象
        auth_config = AuthConfig(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost:8000/callback"
        )
        
        # 验证属性
        self.assertEqual(auth_config.client_id, "test_client_id")
        self.assertEqual(auth_config.client_secret, "test_client_secret")
        self.assertEqual(auth_config.redirect_uri, "http://localhost:8000/callback")
        self.assertIsNone(auth_config.scope)
        self.assertIsNone(auth_config.state)
        self.assertFalse(auth_config.ignore_check_state)
        
    def test_create_auth_config_with_optional_params(self):
        """
        测试创建带可选参数的AuthConfig对象
        """
        # 创建AuthConfig对象
        auth_config = AuthConfig(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost:8000/callback",
            scope="user repo",
            state="test_state",
            ignore_check_state=True
        )
        
        # 验证属性
        self.assertEqual(auth_config.client_id, "test_client_id")
        self.assertEqual(auth_config.client_secret, "test_client_secret")
        self.assertEqual(auth_config.redirect_uri, "http://localhost:8000/callback")
        self.assertEqual(auth_config.scope, "user repo")
        self.assertEqual(auth_config.state, "test_state")
        self.assertTrue(auth_config.ignore_check_state)
        
    def test_create_auth_config_with_missing_required_params(self):
        """
        测试创建缺少必须参数的AuthConfig对象
        """
        # 测试缺少client_id
        with self.assertRaises(ValueError):
            AuthConfig(
                client_id="",
                client_secret="test_client_secret",
                redirect_uri="http://localhost:8000/callback"
            )
            
        # 测试缺少client_secret
        with self.assertRaises(ValueError):
            AuthConfig(
                client_id="test_client_id",
                client_secret="",
                redirect_uri="http://localhost:8000/callback"
            )
            
        # 测试缺少redirect_uri
        with self.assertRaises(ValueError):
            AuthConfig(
                client_id="test_client_id",
                client_secret="test_client_secret",
                redirect_uri=""
            )


if __name__ == "__main__":
    unittest.main() 